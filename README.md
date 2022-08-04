# zoResearcher
## A notes and annotation manager built on top of [Zotero](http://zotero.com/)
### Uses
***Zotero* is a fantastic resource for keeping track of source metadata and citations. But when it comes to note-taking, it's lacking.** **ZoResearcher** takes the sources in your Zotero library, extracts any annotations from associated PDFs and displays them in an easy-to-use interface. For a given project, keep all you notes in an accessible place that updates alongside your research.
- Organize sources by Zotero collection
- Automatically extract annotations from source PDFs
- Add notes for each source
---
### Installation

`
pip install zoresearcher
`
---
### How to use
`
import zoresearcher
`

`
zoresearcher.open(zotero_folder_location, zotero_collection_name=all)
`

- **zotero_folder_location**
	- Filepath for Zotero folder installed on your system.
	- Ex: C:\\Users\\Username\\Zotero


- **zotero_collection_name, default all**
	- Name of Zotero collection for start-up. Defaults to sources in **all** collections. Multiple words permitted. Case agnostic.
	- Ex: My Research Project

---
### Interface
![Interface](/screenshots/interface.png "Interface")
---
### Source annotations
![Annotations](/screenshots/annotated_source.png "Annotations")
---
### Adding notes
![Notes](/screenshots/adding_notes.png "Notes")
### Starring a source
![Starred](/screenshots/starred_sources.png "Starred")
