## Configuration
Python : version **3.14**<br>
Install registered requirements using **pip install -r requirements.txt**<br>
Rename the **.env.example** file, **.env**<br>

### Env file<br>
DHIS2_BASE_URL="http://dhis.com/api"<br>
DHIS2_USERNAME="username"<br>
DHIS2_PASSWORD="password"<br>
REPORTS_DIRECTORY ="./reports"<br>
CASE_NUMBER_COLUMN_ID =""<br>

## List of requirements
-   blinker==1.9.0
-   certifi==2026.1.4
-   charset-normalizer==3.4.4
-   click==8.3.1
-   colorama==0.4.6
-   et_xmlfile==2.0.0
-   idna==3.11
-   itsdangerous==2.2.0
-   Jinja2==3.1.6
-   MarkupSafe==3.0.3
-   numpy==2.4.2
-   openpyxl==3.1.5
-   packaging==26.0
-   python-dateutil==2.9.0.post0
-   python-dotenv==1.2.1
-   requests==2.32.5
-   six==1.17.0
-   tzdata==2025.3
-   urllib3==2.6.3
-   Werkzeug==3.1.5

## Scripts index 
[Clone dashboard](#clone-dashboard)<br>
[Dashboard_org_unit_edit](#dashboard-org-unit-edit)<br>
[Edit event](#edit-event)<br>
[Tracked entity instance report](#tracked-entity-instance-report)<br>

## Clone dashboard
Cloning a dashboard requires two login credentials.<br>
Once the identifies for each dashboard are entered, the content of the first one will be copied and transferred to the second. If the destination dashboard is not empty, a message will appear offering you the option to cancel the operation or add the elements from the source dashboard to the bottom of the destination dashboard.<br>
If the destination dashboard is empty, it will be structured in the same way as the source dashboard, including the position and size of the elements.<br>
A **JSON** file for the cloned dashboard is created after this operation.<br>
**! Some types of elements cannot be copied in their entirety, including informational items.**

### Required inputs
-    Source dashboard ID (dashboard to clone)
-    Destination dashboard ID (dashboard receiving the duplicated structure)

## Dashboard org unit edit
This script allows you to change the organization unit for a set of selected dashboard's items.<br>
The selection is duplicated using a generated UID.<br>
Each item is then listed throught outputs on the user terminal command. Once selected, the item(s) will be submitted for changes.<br>
### Changes
**Title** : the title of the selected item(s) can be replaced to match the new organization unit choice. The three most common titles present in the selection will be displayed for change.<br>
**Organization units** : one or multiple organization units IDs can be entered by the user to update the selected item from the numbered list.<br>
**Position** : the position and size of each element remain unchanged after the updates.<br><br>

After the operation is done, a **JSON** file is generated in the report folder.

### Required inputs
-    Dashboard ID
-    Items on which the organisation unit will be changed (one, multiple, or all)
-    New item title changes (not required)
-    New organisation unit (one or multiple)

## Edit event
Each event is linked to a set of data elements. Using the event ID, a list of data elements is displayed for selection.<br>
Data element value can be modified one by one. A confirmation message is sent to the user before every change.<br>
As a result, an **xlsx** file will be created displaying the old and new values for the selected event and its elements.

### Required inputs
-    Event ID
-    Data element (list)
-    New value for the selected data element

## Tracked entity instance report

This report is made to assess the programs in which the patient is admitted and discharged the same day. It will compare the date of the first and last event for each tracked entity instance within a date range. To check if the patient has been discharged the same day as his admission, the script will provide an **xlsx** file displaying the tracked entity instance attributes and a status.<br>

### Required inputs
-    Program ID
-    Organisation unit ID
-    Date of the enrollment
-    Date of the last registered event
-    Data element ID (list)<br>

### Available status<br>
Same admission and discharge date <svg width="100" height="12"><rect width="100" height="12" fill="#4caf50" rx="4" /></svg>

Discharge date different from admission date <svg width="100" height="12"><rect width="100" height="12" fill="#f44336" rx="4" />
</svg>

Admission date registered after discharge date <svg width="100" height="12"><rect width="100" height="12" fill="#ff9800" rx="4" /></svg>

Missing data  <svg width="100" height="12"><rect width="100" height="12" fill="#9e9e9e" rx="4" /></svg>


The report is provided with already selected columns, including
-    TEI ID
-    Case number
-    Organisation unit
-    Admission and discharge result