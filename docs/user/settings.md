# Settings

**Settings...** in the tray menu opens a config editor: a tree of all values with their
types, where you edit a value in place. Use **Save** to write the change to your config
file, and **Undo** / **Redo** to step back. The editor is not modal, so the app keeps
working while it is open. Closing it with unsaved changes asks what to do with them.

Saved changes apply right away, there is no need to restart the app. Changing the check
frequency restarts the check timer.

## Available settings

| Setting | Default | Meaning |
| --- | --- | --- |
| `cards_tracker.frequency_min` | `60` | Minutes between background checks. At least `1`. |
| `cards_tracker.history_size` | `20` | How many checks to keep in the history. At least `10`. |
| `pushover.enabled` | `false` | Send a push notification when new cards are found. |
| `pushover.user_key` | empty | Your Pushover user key. |
| `pushover.app_key` | empty | The API token of your Pushover application. |

Please do not set the frequency too low. The store rate limits requests, and a failed check
is only retried on the next scheduled one.

## Editing the file directly

The settings are stored in `~/.config/HazbinTracker/config.json`, you can also edit that
file with a text editor while the app is not running:

```json
{
  "cards_tracker": {
    "frequency_min": 60,
    "history_size": 20
  },
  "pushover": {
    "enabled": false,
    "user_key": "",
    "app_key": ""
  }
}
```

Only the values that differ from the defaults are written to the file.
