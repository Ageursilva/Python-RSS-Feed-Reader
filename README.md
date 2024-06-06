# Python RSS Feed Reader with Tkinter GUI

This Python program is a robust and user-friendly RSS feed reader, featuring a graphical user interface (GUI) built with Tkinter. It offers a range of functionalities to enhance your RSS feed reading experience:

## Features

### Import Feeds from OPML Files
- Easily add multiple feeds by importing them from an OPML file.

### Subscribe to Feeds
- Add new feeds by entering their URLs manually.

### Update Feeds
- Refresh the list of news articles from subscribed feeds.

### View Feed Content
- See a list of titles and links from the latest articles in subscribed feeds.

### Read Full Articles
- Clicking on a title opens the corresponding article in the web browser.

### View Article Description (Optional)
- Right-clicking on a title displays a popup window with the full article description (if available in the feed).

### Manage Feeds
- A separate window allows you to view a list of all subscribed feeds, including their IDs and URLs. You can also delete feeds you no longer want to follow from this window.

## Key Features

- Easy to use and navigate with a clear GUI.
- Utilizes SQLite database for storing feed data and articles (if descriptions are retrieved).
- Tkinter offers a native desktop application experience.
- Supports importing feeds from OPML files.

## Getting Started

1. Clone this repository or download the code files.
2. Install the required Python libraries using `pip install tkinter feedparser opml sqlite3 xml.etree ElementTree webbrowser threading`.
3. (Optional) Add an icon file named `icone.ico` to the root directory of the project for a custom application icon.
4. Run the program by executing `main.py`.

## Further Enhancements

This code provides a solid foundation for a feature-rich RSS feed reader. Here are some potential improvements you can explore:

- Implement a mechanism to schedule automatic feed updates at regular intervals.
- Add the ability to categorize feeds for better organization.
- Integrate with feedly or other online feed management services for synchronization.
- Consider using a more advanced layout for the listbox to display titles and descriptions together.

## Contribution

Contributions are welcome! Feel free to open issues and pull requests.

## License

This project is licensed under the [MIT License](LICENSE).