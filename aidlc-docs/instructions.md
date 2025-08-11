# AI-DLC Workflow

## Inception

### Intent to User Stories
Your Role: You are an expert product manager. You are tasked with creating well defined user stories that become the contract for developing the system as described in the Task section below. 

Plan for the work ahead and write your steps in the aidlc-docs/inception/user_stories_plan.md file with checkboxes for each step in the plan. If any step needs my clarification, add the questions with the [Question] tag and create an empty [Answer] tag for me to fill the answer. Do not make any assumptions or decisions on your own. Upon creating the plan, ask for my review and approval. After my approval, you can go ahead to execute the same plan one step at a time. Once you finish each step, mark the checkboxes as completed in the plan.

Your Task: Doctors register their medical specialties and availability schedules. Patients book appointments by describing their symptoms and health concerns. System matches patient appointment requests with the most suitable Doctors based on medical specialties and available time slots. Patients choose a Doctor from the system recommended options. The objective of this doctor appointment platform is to connect patients with the right medical specialists faster and more efficiently.

### Stories to Units


Your Role: You are an experienced software architect. You are tasked with understanding the user stories of a full system as in the Task section. You will group the stories into multiple units of work that can be implemented in parallel. Each unit contains highly cohesive user stories that can be built by a single team. An unit is equivalent to bounded contexts in domain driven design and is aligned to a particular subdomain or specific business roles. For each unit, write their respective user stories and acceptance criteria in individual md files in the aidlc-docs/inception/units/ folder. Don't generate any additional design details. 

Plan for the work ahead and write your steps in the iaidlc-docs/nception/units/units_plan.md file with checkboxes for each step in the plan. If any step needs my clarification, add the questions with the [Question] tag and create an empty [Answer] tag for me to fill the answer. Do not make any assumptions or decisions on your own. Upon creating the plan, ask for my review and approval. After my approval, you can go ahead to execute the same plan one step at a time. Once you finish each step, mark the checkboxes as completed in the plan.

Your Task: Refer to the user stories in the aidlc-docs/inception/comprehensive_user_stories.md folder.


### Shared Data Models

Your Role: You are an experienced software architect. You are tasked with creating the component model.

Plan for the work ahead and write your steps in the aidlc-docs/inception/units/dependencies_integration_summary.md file with checkboxes for each step in the plan. If any step needs my clarification, add the questions with the [Question] tag and create an empty [Answer] tag for me to fill the answer. Do not make any assumptions or decisions on your own. Upon creating the plan, ask for my review and approval. After my approval, you can go ahead to execute the same plan one step at a time. Once you finish each step, mark the checkboxes as completed in the plan.

Your Task: Refer to the Shared Data Models section in aidlc-docs/inception/dependencies_integration_summary.md folder. Create the component model for each of the core entities with their attributes. Refer to aidlc-docs/inception/comprehensive_user_stories.md for additional context. Save the output in aidlc-docs/inception/units/shared_model.md



## Construction

### Domain Modelling

Your Role: You are an experienced software engineer. You are tasked with designing the Domain Model to implement all the user stories as referred in the Task section. This model shall contain all the components, the attributes, the behaviours and how the components interact to implement business logic in the user stories. Do not generate any architectural components. Do not generate any codes. Strictly refer and copy the full definition of relevant shared components needed as present in the aidlc-docs/inception/units/shared_model.md. Write the component model into a separate md file in the aidlc-docs/construction folder.

Plan for the work ahead and write your steps in the aidlc-docs/construction/domain_model_plan_user_management_service.md file with checkboxes for each step in the plan. If any step needs my clarification, add the questions with the [Question] tag and create an empty [Answer] tag for me to fill the answer. Do not make any assumptions or decisions on your own. Upon creating the plan, ask for my review and approval. After my approval, you can go ahead to execute the same plan one step at a time. Once you finish each step, mark the checkboxes as completed in the plan.

Your Task: Refer to the user stories in the aidlc-docs/inception/units/user_management_service.md

### Dmain Model to Code

Your Role: You are an experienced software engineer. Your task is as mentioned in the Task section below. Plan for the work ahead and write your steps in the aidlc-docs/construction/domain_code_plan_user_management_service.md file with checkboxes for each step in the plan. If any step needs my clarification, add the questions with the [Question] tag and create an empty [Answer] tag for me to fill the answer. Do not make any assumptions or decisions on your own. Upon creating the plan, ask for my review and approval. After my approval, you can go ahead to execute the same plan one step at a time. Once you finish each step, mark the checkboxes as completed in the plan.

Task: Refer to aidlc-docs/construction/domain_model_user_management_service.md file. Generate a very simple and intuitive Python implementation for the components in the domain model. Keep the directory structure flat. Reuse standard python components available for loggic and other utulities. Assume the repositories are in-memory. Generate the classes in respective individual files.


### Adding Architectural Components

Your Role: You are an experienced software architect. Your task is as mentioned in the Task section below. Plan for the work ahead and write your steps in the aidlc-docs/construction/architecture_plan.md file with checkboxes for each step in the plan. If any step needs my clarification, add the questions with the [Question] tag and create an empty [Answer] tag for me to fill the answer. Do not make any assumptions or decisions on your own. Upon creating the plan, ask for my review and approval. After my approval, you can go ahead to execute the same plan one step at a time. Once you finish each step, mark the checkboxes as completed in the plan.

Task: Refer to text_enhancement/text_enhancement_service.py. I want to expose enhance_content method to be consumed by clients over the internet. This service will be hosted on AWS. Use AWS Well Architected Principles and select the packaging and deployment option.