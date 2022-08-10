# zoResearch
## A notes and annotation manager built on top of [Zotero](http://zotero.com/)
### Uses
***Zotero* is a fantastic resource for keeping track of source metadata and citations. But when it comes to note-taking, it's lacking.** 

**ZoResearch** takes the sources in your Zotero library, extracts any annotations from associated PDFs and displays them in an easy-to-use interface. For a given project, keep all you notes in an accessible place that updates alongside your research.
- Organize sources by Zotero collection
- Automatically extract annotations from source PDFs
- Add notes for each source
---
### Installation

`
pip install zoresearch
`
---
### How to use
`
import zoresearch
`

`
zoresearch.open(zotero_folder_location, zotero_collection_name=all)
`

**zotero_folder_location**

- Filepath for Zotero folder installed on your system.

- Ex: C:\\Users\\Username\\Zotero

**zotero_collection_name, default all**

- Name of Zotero collection for start-up. Defaults to sources in **all** collections. Multiple words permitted. Case agnostic.

- Ex: My Research Project

---
### Interface
Zotero sources are displayed on a scrollable sidebar. The main window displays the selected source with user-generated notes as well as citations from the source's associated PDF (if any). 

- Use dropdown menus to select different Zotero collections and to filter sources by either 'Starred' or 'Unread'.

- Click 'Show PDF' for thumbnails.

![Interface](/screenshots/interface.png "Interface")
---
### Source annotations
Highlighting and adding comments to PDFs are convenient ways to take notes. But extracting them can be a pain! zoResearch extracts all these annotations for easy access.

- Annotations are labeled with their absolute page number in the associated PDF and type (highlight, sticky note).

- New annotations are added at zoResearch startup.

![Annotations](/screenshots/annotated_source.png "Annotations")
---
### Adding notes
In addition to PDF annotations, users can add additional notes directly to the viewer. 

- zoResearch automatically saves these notes.

![Notes](/screenshots/adding_notes.png "Notes")
---
### Starring a source
Want to designate some important sources? Simply 'Star' the source so that you can easily find them using the dropdown menu.

![Starred](/screenshots/starred_sources.png "Starred")
