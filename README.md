# Hoos Give Back

Led a team of five as a Software Architect to create a Project Management Application (PMA) for UVA's CIOs (Contracted Independent Organization) open to the 20,000+ students at UVA. Developed under SCRUM methodologies.

## Features and Functionalities

- Site account creation and login system using Google OAuth API
- Create and delete your own projects with a title, description, collaborators, start and end date, viewable on the site's calendar
- Add project collaborators to your project after its creation
- Request to join projects you aren't in
- Approve or deny join requests as a project owner
- Transfer project ownership as a project owner
- Upload and delete documents and images to your project(s) which will be securely stored using Amazon S3
- File search feature - add document titles, keywords, and other metadata/search terms to uploaded files in order to search for files uploaded to a project
- Live messaging within a project to communicate with collaborators
- Project to-do list, add and keep track of complete and incomplete tasks
- Share a project on Facebook

### User Types

- Anonymous User: View all projects by title and description only, unable to see the contents of projects, join, or create any of their own
- Common User: Create your own project or request to join a project and see all projects categorized as projects you own, are in, or aren't in
- Common User - Project Collaborator: All permissions of a Common User, with the ability to upload documents within a project, delete their own documents, view all documents, search for any document, chat within the project, add tasks to do, and leave the project
- Common User - Project Owner: All permissions of a Common User - Project Collaborator with additional abilities such as being able to add collaborators, approve or deny join requests, transfer project ownership, and delete the project
- PMA Site Admin: See all contents of the PMA site (however, unable to join or create projects), with moderation powers of deleting any file or project
- Django Admin: Manage all contents of the PMA site (projects, users, documents, chats, all of which are timestamped) and be able to promote a common user to a PMA site admin

### Technologies Used

- Frontend: HTMX, Bootstrap, TailwindCSS
- Backend: Django
- Database: PostgreSQL
- Cloud Services: Heroku (site deployment), Amazon S3 (file storage)
- Authentication: Google OAuth 2.0

### Setup Instructions

This repo is set up to allow you to customize how you want to run it, locally or deployed on a cloud service. If you're running locally, I highly recommend setting up a virtual environment `python -m venv myenvname` and activating it with `myenvname\Scrpits\activate`. Install the requirements on there with `pip install -r requirements.txt`.

Everything you need to customize will be in `pmaproject/settings.py` for database configuration, allowed hosts, Amazon S3 setup, and keys needed to interact with Google OAuth 2.0 API. Simply change the dummy values of the variables to actual values that will work. Additionally, key values for Google OAuth will be needed in lines 22-24 of `communityservice/views.py`.

`.github/workflows/django.yml` for Continuous Integration with GitHub Actions. Currently cleared and reset for a fresh repo clone, which will show as failing under this branch.
