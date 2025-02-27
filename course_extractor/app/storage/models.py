from datetime import datetime, UTC


class CourseDocument:
    def __init__(self, doc_id, file_name, file_path, file_type="pdf", title=None, url=None,
                 pages=None, views=None, text=None, tags=None):
        """
        Initialize a CourseDocument object based on the structure used in scraper.py.

        Args:
            doc_id (int/str): Unique ID of the document.
            file_name (str): Name of the file.
            file_path (str): Path to the file relative to download directory.
            file_type (str): Type of the file (default: "pdf").
            title (str): Title of the document.
            url (str): Original URL of the document.
            pages (int): Number of pages in the document.
            views (int): Number of views for the document.
            text (str): Extracted text content from the document.
            tags (list): List of tags for categorization.
        """
        self._id = doc_id
        self.file_name = file_name
        self.file_path = file_path
        self.file_type = file_type
        self.title = title
        self.url = url
        self.pages = pages
        self.views = views
        self.text = text
        self.tags = tags or []
        self.creation_date = datetime.now(UTC)

    def to_dict(self):
        """
        Convert the CourseDocument object to a dictionary for MongoDB storage.

        Returns:
            dict: A dictionary representation of the document.
        """
        return {
            "_id": self._id,
            "file_name": self.file_name,
            "file_path": self.file_path,
            "file_type": self.file_type,
            "title": self.title,
            "url": self.url,
            "pages": self.pages,
            "views": self.views,
            "text": self.text,
            "tags": self.tags,
            "creation_date": self.creation_date
        }

    @classmethod
    def from_scraper_data(cls, doc_data, text=None):
        """
        Create a CourseDocument instance from data structure used in scraper.py.

        Args:
            doc_data (dict): Document data from scraper.
            text (str, optional): Extracted text to include.

        Returns:
            CourseDocument: A new CourseDocument instance.
        """
        return cls(
            doc_id=doc_data["_id"],
            file_name=doc_data["file_name"],
            file_path=doc_data["file_path"],
            file_type=doc_data.get("file_type", "pdf"),
            title=doc_data.get("title"),
            url=doc_data.get("url"),
            pages=doc_data.get("pages"),
            views=doc_data.get("views"),
            text=text
        )