## To Do
<img align="right" width="40%" height="40%" src="https://the-public-domain-review.imgix.net/collections/ernst-haeckels-jellyfish/42421213172_83205edde2_b.jpg?fit=max&w=2400">

### Back end
- [x] Dropdown menu for collections to switch collections
- [x] Save project data to JSON (including when switching collections)
- [x] Block collection switching while background update is running
- [x] Prevent multiple instances of program
- [ ] Program not running all the way through when database is first created
- [ ] Timeout wrapper for HTML conversion (maybe unnecessary)
- [ ] Starring option
	- Add Star dummy where 'read' is added for new sources
	- Change source sort to prioritize star
	- Add star icon/symbol
- [ ] Change color for unread sources
	- In GUI, change title for unread to 'NEW:'
	- Change Hover/Leave behavior
	- Add fg change to read status change function
- [ ] Source search
	- Look up examples
- [ ] Add 'All' collection
	- Create 'All' collection
	- Make 'All' start of alphabetical collection dropdown list
	- Change startup to 'All' PROBABLY NOT
- [ ] Source label object class
	Functions:
		1. Hover
		2. Leave hover
		3. Click (display source)
		4. Star
		5. Change read status
		6. Open PDF
	Requirements:
		1. Label widget
		2. Source metadata

### Organization
- [ ] Clean up main modules for db.py & notes_app.py
- [ ] Change name of db.py to research.py
- [ ] Consider changing functions to classes (maybe create a source class) 
- [ ] Make notes_app.py collection start up its own function call
- [ ] Add Starring function to GUI


### GUI
- [x] Remove whitespace from beginning of printed source['all_notes']
- [x] Sort sources in collection by date, read status
- [X] Read status button (which also sorts collections)
- [x] Add ctrl+w exit option
- [x] Capitalize collections in dropdown and exclude extra collections (if possible)
- [x] Dragging slide down of sources
<img align="center" width="75%" height="75%" src="https://the-public-domain-review.imgix.net/essays/o-uommibatto-how-the-pre-raphaelites-became-obsessed-with-the-wombat/46679785221_d4e9613991_c.jpg?fit=max&w=1200&h=850">


## Complete
 - #### Create single database
	- [x] 1. Create source list from Zotero
	- [x] 2. Check source list against app dictionary for new sources
		- [x] 1. Check key against key
		- [x] 2. Add new sources if needed
		- [x] 3. See if Zotero source key is in notes dict
			- if no: 
				add meta-data
			- if yes:
				replace notes dict collections with Zotero collections (in case they've changed)
		- [x] 4. Delete sources that have been removed
	- [x] 3. Get list of sources from queried collection
		- [x] 1. Convert files for new sources
		- [x] 2. Check for highlights for all sources
	- [x] 4. Open GUI with queried collection
		What does GUI need?
		1. Data for sources in selected collection
		2. List of collections
			a) Can be appended to end of JSON with room for all notes? Need to figure out where to save general notes
			b) When collection is changed, needs access to other collection data
				When colleciton is changed, make sure it's updated in db.py
		So give it the whole dataset and the selected collection name
		GUI creates dropdown of collection names
		When user switches, wait for signal or something
		Potential issue - saving data/exiting GUI while other sources are still being updated
		- [x] 1. For all other sources (in background):
		- [x] 2. Update highlights
		- [x] 3. Convert files (for new)
 	- [x] Sources not showing parent collection (ex. 'reading' but not 'interest')




