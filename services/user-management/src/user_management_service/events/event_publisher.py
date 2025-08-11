"""
Event publisher and repository for the User Management Service.
"""

import json
import queue
import threading
import time
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Union
from uuid import UUID

from ..repositories.base_repository import InMemoryRepository
from .user_events import UserRegistrationEvent, ProfileUpdateEvent, AvailabilityUpdateEvent
from ..utils.enums import EventStatus
from ..utils.exceptions import IntegrationError
from ..utils.base_models import RetryConfig, CircuitBreakerState

# Type alias for all event types
EventType = Union[UserRegistrationEvent, ProfileUpdateEvent, AvailabilityUpdateEvent]


class EventRepository(InMemoryRepository[EventType]):
    """Repository for all event types."""
    
    def __init__(self):
        """Initialize the event repository."""
        super().__init__("Event", "events.json")
    
    def _deserialize_entity(self, data: Dict[str, Any]) -> EventType:
        """Deserialize event from dictionary data based on event type."""
        event_type = data.get('event_type')
        
        if event_type == 'user_registered':
            return UserRegistrationEvent.from_dict(data)
        elif event_type == 'profile_updated':
            return ProfileUpdateEvent.from_dict(data)
        elif event_type == 'availability_updated':
            return AvailabilityUpdateEvent.from_dict(data)
        else:
            raise ValueError(f"Unknown event type: {event_type}")
    
    def find_by_event_type(self, event_type: str) -> List[EventType]:
        """Find events by event type."""
        return self.find_by_field("event_type", event_type)
    
    def find_by_user_id(self, user_id: UUID) -> List[EventType]:
        """Find events by user ID."""
        results = []
        for event in self.find_all():
            if hasattr(event, 'user_id') and event.user_id == user_id:
                results.append(event)
        return results
    
    def find_by_status(self, status: EventStatus) -> List[EventType]:
        """Find events by status."""
        return self.find_by_field("status", status)
    
    def find_pending_events(self) -> List[EventType]:
        """Find all pending events."""
        return self.find_by_status(EventStatus.PENDING)
    
    def find_failed_events(self) -> List[EventType]:
        """Find all failed events."""
        return self.find_by_status(EventStatus.FAILED)
    
    def find_events_by_correlation_id(self, correlation_id: UUID) -> List[EventType]:
        """Find events by correlation ID."""
        return self.find_by_field("correlation_id", correlation_id)
    
    def find_events_by_date_range(self, start_date: datetime, end_date: datetime) -> List[EventType]:
        """Find events within a date range."""
        results = []
        for event in self.find_all():
            if start_date <= event.timestamp <= end_date:
                results.append(event)
        return sorted(results, key=lambda e: e.timestamp)
    
    def get_event_statistics(self) -> Dict[str, Any]:
        """Get event processing statistics."""
        all_events = self.find_all()
        pending_events = self.find_pending_events()
        failed_events = self.find_failed_events()
        processed_events = self.find_by_status(EventStatus.PROCESSED)
        
        # Count by event type
        type_counts = {}
        for event in all_events:
            event_type = event.event_type
            type_counts[event_type] = type_counts.get(event_type, 0) + 1
        
        # Calculate processing rate
        total_processable = len(all_events) - len(pending_events)
        success_rate = (len(processed_events) / total_processable * 100) if total_processable > 0 else 0
        
        return {
            'total_events': len(all_events),
            'pending_events': len(pending_events),
            'processed_events': len(processed_events),
            'failed_events': len(failed_events),
            'success_rate': round(success_rate, 1),
            'event_type_distribution': type_counts
        }


class EventPublisher:
    """Event publisher with queue-based processing and retry logic."""
    
    def __init__(self, event_repository: EventRepository):
        """Initialize the event publisher."""
        self.event_repository = event_repository
        self.event_queue = queue.Queue()
        self.retry_config = RetryConfig()
        self.circuit_breaker = CircuitBreakerState()
        self.is_running = False
        self.worker_thread = None
        
        # Event handlers registry
        self.event_handlers: Dict[str, List[callable]] = {
            'user_registered': [],
            'profile_updated': [],
            'availability_updated': []
        }
    
    def register_handler(self, event_type: str, handler: callable) -> None:
        """Register an event handler."""
        if event_type in self.event_handlers:
            self.event_handlers[event_type].append(handler)
        else:
            self.event_handlers[event_type] = [handler]
    
    def publish_event(self, event: EventType) -> None:
        """Publish an event to the queue."""
        # Store event in repository
        self.event_repository.create(event)
        
        # Add to processing queue
        self.event_queue.put(event)
    
    def publish_user_registration_event(self, user_id: UUID, user_type: str, 
                                      email: str, name: str) -> UserRegistrationEvent:
        """Publish a user registration event."""
        from ..utils.enums import UserType
        
        event = UserRegistrationEvent(
            user_id=user_id,
            user_type=UserType(user_type),
            email=email,
            name=name
        )
        
        self.publish_event(event)
        return event
    
    def publish_profile_update_event(self, user_id: UUID, user_type: str,
                                   previous_values: Dict[str, Any],
                                   new_values: Dict[str, Any],
                                   updated_by: Optional[UUID] = None) -> ProfileUpdateEvent:
        """Publish a profile update event."""
        from ..utils.enums import UserType
        
        event = ProfileUpdateEvent(
            user_id=user_id,
            user_type=UserType(user_type),
            updated_by=updated_by
        )
        event.set_changes(previous_values, new_values)
        
        self.publish_event(event)
        return event
    
    def publish_availability_update_event(self, doctor_id: UUID, availability_id: UUID,
                                        change_type: str, previous_data: Optional[Dict[str, Any]],
                                        new_data: Optional[Dict[str, Any]],
                                        updated_by: Optional[UUID] = None) -> AvailabilityUpdateEvent:
        """Publish an availability update event."""
        from ..utils.enums import ChangeType
        
        event = AvailabilityUpdateEvent(
            doctor_id=doctor_id,
            availability_id=availability_id,
            change_type=ChangeType(change_type),
            updated_by=updated_by
        )
        event.set_availability_data(previous_data, new_data)
        
        self.publish_event(event)
        return event
    
    def start_processing(self) -> None:
        """Start the event processing worker thread."""
        if not self.is_running:
            self.is_running = True
            self.worker_thread = threading.Thread(target=self._process_events, daemon=True)
            self.worker_thread.start()
    
    def stop_processing(self) -> None:
        """Stop the event processing worker thread."""
        self.is_running = False
        if self.worker_thread:
            self.worker_thread.join(timeout=5)
    
    def _process_events(self) -> None:
        """Process events from the queue."""
        while self.is_running:
            try:
                # Get event from queue with timeout
                event = self.event_queue.get(timeout=1)
                
                # Check circuit breaker
                if self.circuit_breaker.is_open:
                    # Skip processing if circuit breaker is open
                    time.sleep(1)
                    continue
                
                # Process the event
                self._process_single_event(event)
                
            except queue.Empty:
                # No events to process, continue
                continue
            except Exception as e:
                print(f"Error in event processing loop: {e}")
                time.sleep(1)
    
    def _process_single_event(self, event: EventType) -> None:
        """Process a single event with retry logic."""
        max_attempts = self.retry_config.max_attempts
        
        for attempt in range(1, max_attempts + 1):
            try:
                # Call event handlers
                handlers = self.event_handlers.get(event.event_type, [])
                for handler in handlers:
                    handler(event)
                
                # Mark event as processed
                event.mark_processed()
                self.event_repository.update(event)
                
                # Record success for circuit breaker
                self.circuit_breaker.record_success()
                return
                
            except Exception as e:
                error_message = f"Attempt {attempt}/{max_attempts} failed: {str(e)}"
                print(f"Event processing error: {error_message}")
                
                # Record failure for circuit breaker
                self.circuit_breaker.record_failure()
                
                if attempt == max_attempts:
                    # Final attempt failed, mark event as failed
                    event.mark_failed(error_message)
                    self.event_repository.update(event)
                else:
                    # Wait before retry
                    delay = self.retry_config.get_delay(attempt)
                    time.sleep(delay)
    
    def process_pending_events(self) -> Dict[str, int]:
        """Process all pending events (useful for batch processing)."""
        pending_events = self.event_repository.find_pending_events()
        
        results = {
            'processed': 0,
            'failed': 0,
            'skipped': 0
        }
        
        for event in pending_events:
            try:
                self._process_single_event(event)
                if event.is_processed():
                    results['processed'] += 1
                elif event.is_failed():
                    results['failed'] += 1
                else:
                    results['skipped'] += 1
            except Exception as e:
                print(f"Error processing event {event.id}: {e}")
                results['failed'] += 1
        
        return results
    
    def retry_failed_events(self, max_age_hours: int = 24) -> Dict[str, int]:
        """Retry failed events that are not too old."""
        cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
        failed_events = self.event_repository.find_failed_events()
        
        results = {
            'retried': 0,
            'skipped_too_old': 0,
            'processed': 0,
            'failed_again': 0
        }
        
        for event in failed_events:
            if event.timestamp < cutoff_time:
                results['skipped_too_old'] += 1
                continue
            
            # Reset event status to pending for retry
            event.status = EventStatus.PENDING
            event.error_message = None
            self.event_repository.update(event)
            
            # Process the event
            try:
                self._process_single_event(event)
                if event.is_processed():
                    results['processed'] += 1
                else:
                    results['failed_again'] += 1
                results['retried'] += 1
            except Exception as e:
                print(f"Error retrying event {event.id}: {e}")
                results['failed_again'] += 1
        
        return results
    
    def get_queue_size(self) -> int:
        """Get the current queue size."""
        return self.event_queue.qsize()
    
    def clear_queue(self) -> int:
        """Clear the event queue and return the number of cleared events."""
        cleared_count = 0
        while not self.event_queue.empty():
            try:
                self.event_queue.get_nowait()
                cleared_count += 1
            except queue.Empty:
                break
        return cleared_count


# Default event handlers (can be overridden)
def default_user_registration_handler(event: UserRegistrationEvent) -> None:
    """Default handler for user registration events."""
    print(f"Processing user registration: {event.name} ({event.email}) - {event.user_type.value}")


def default_profile_update_handler(event: ProfileUpdateEvent) -> None:
    """Default handler for profile update events."""
    print(f"Processing profile update for user {event.user_id}: {event.changed_fields}")


def default_availability_update_handler(event: AvailabilityUpdateEvent) -> None:
    """Default handler for availability update events."""
    print(f"Processing availability update for doctor {event.doctor_id}: {event.change_type.value}")


# Global event publisher instance (singleton pattern)
_event_publisher_instance = None


def get_event_publisher() -> EventPublisher:
    """Get the global event publisher instance."""
    global _event_publisher_instance
    if _event_publisher_instance is None:
        event_repository = EventRepository()
        _event_publisher_instance = EventPublisher(event_repository)
        
        # Register default handlers
        _event_publisher_instance.register_handler('user_registered', default_user_registration_handler)
        _event_publisher_instance.register_handler('profile_updated', default_profile_update_handler)
        _event_publisher_instance.register_handler('availability_updated', default_availability_update_handler)
        
        # Start processing
        _event_publisher_instance.start_processing()
    
    return _event_publisher_instance