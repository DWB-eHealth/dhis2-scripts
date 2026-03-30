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
Cloning a dashboard can only be done by creating an empty one. This gives an ID to be used by the script.
Once a destination ID available, every element from the source dashboard would be copied.<br>
If the destination dashboard is not empty, a message will be displayed to either cancel the operation, or add the items from the source dahsboard at the bottom of the destination one.<br>
A **json** file for the cloned dashboard is created as a result of this operation.

### Required inputs
-    Source dashboard ID (dashboard to clone)
-    Destination dashboard ID (dashboard receiving the copied content)


## Dashboard org unit edit
This script intends to change the organisation unit of one or multiple elements within a dashboard. 
Each item has a number attributed to it to enter as an input.<br>
This will create new duplicated items with a different organisation unit in the destination dashboard.
The title for the selected set of items can be changed based on a list of the three most common titles available. Those could be modified to match the newly entered organisation unit.

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
Same admission and discharge date <span style="display:inline-block;width:100px;height:10px;background:#4caf50;border-radius:4px;"></span><br>
Discharge date different from admission date <span style="display:inline-block;width:100px;height:10px;background:#f44336;border-radius:4px;"></span><br>
Admission date registered after discharge date <span style="display:inline-block;width:100px;height:10px;background:#ff9800;border-radius:4px;"></span><br>
Missing data <span style="display:inline-block;width:100px;height:10px;background:#9e9e9e;border-radius:4px;"></span><br>


The report is provided with required columns, including
-    ID
-    Case number
-    Organisation unit
-    Admission and discharge result