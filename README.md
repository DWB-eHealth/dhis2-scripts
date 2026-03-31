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
-    Destination dashboard ID (dashboard receiving the copied content)


## Dashboard org unit edit
This script allows you to modify the organization units of the elements displayed on a dashboard. <br>
Each item is associated with a numbered list. Once selected by the user, the elements will be duplicated, and their copies will receive the identifier of the entered organizational unit. The position and size of each element remain unchanged.<br>
The title of the selected set of elements can be modified from a list of the three most common titles. These titles can then be adapted to the newly entered organizational unit.<br>
After the operation is done, the new version of the dashboard will be exported as a **JSON** file.

### Required inputs
-    Dashboard ID
-    Items on which the organisation unit will be changed (one, multiple, or all)
-    New item title changes (not required)
-    New organisation unit

## Edit event
An event value can only be changed if the condition entered as an input is true.<br>
As a result, an **xlsx** file will be created displaying the old and new values for the event along with its ID and the data element ID.

### Required inputs
-    Organisation unit ID
-    Data element ID
-    Event ID
-    Condition to meet
-    New value

## Tracked entity instance report

This report is made to assess the programs in which the patient is admitted and discharged the same day. It will compare the date of the first and last event for each tracked entity instance within a date range. To check if the patient has been discharged the same day as his admission, the script will provide an **xlsx** file displaying the tracked entity instance attributes and a status.<br>

### Required inputs
-    Program ID
-    Organisation unit ID
-    Date of the enrollment
-    Date of the last registered event
-    Data element ID (one or multiple)<br>

### Available status<br>
Same admission and discharge date <svg width="100" height="12"><rect width="100" height="12" fill="#4caf50" rx="4"/></svg><br>
Discharge date different from admission date <svg width="100" height="12"><rect width="100" height="12" fill="#f44336" rx="4"/></svg><br>
Admission date registered after discharge date <svg width="100" height="12"><rect width="100" height="12" fill="#ff9800" rx="4"/></svg><br>
Missing data <svg width="100" height="12"><rect width="100" height="12" fill="#9e9e9e" rx="4"/></svg>


The report is provided with required columns, including
-    ID
-    Case number
-    Organisation unit
-    Admission and discharge result