# YouTube API Configuration

This application now supports automatic fetching of the latest livestreams from monitored YouTube channels using the YouTube Data API v3.

## Setup

### 1. Get a YouTube Data API Key

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the YouTube Data API v3
4. Create credentials (API Key)
5. Restrict the API key to YouTube Data API v3 for security

### 2. Configure Environment Variables

Set the following environment variables:

```bash
# Required: Your YouTube Data API key
export YOUTUBE_API_KEY="your_api_key_here"

# Optional: Comma-separated list of YouTube channel IDs to monitor
export MONITORED_CHANNELS="UCxxxxxx,UCyyyyyy,UCzzzzzz"
```

### 3. Find Channel IDs

To find a YouTube channel ID:
1. Go to the channel's page
2. View page source and search for "channelId" 
3. Or use the URL format: `https://www.youtube.com/channel/CHANNEL_ID`

## Usage

### Automatic Refresh

When properly configured, the application will:
- Show a "Refresh from YouTube" button in the stream management panel
- Display the last update timestamp
- Allow manual refresh of livestreams from monitored channels

### API Endpoints

- `GET /api/status` - Check configuration status
- `POST /api/refresh-streams` - Manually refresh streams from YouTube API

### Manual Stream Management

You can still manually add/remove streams using the existing interface, even without YouTube API configuration.

## Error Handling

- If YouTube API key is not configured, the refresh functionality will be hidden
- If no monitored channels are configured, refresh will return an error
- API failures are handled gracefully with user-friendly error messages

## Example Configuration

```bash
# For equipment monitoring streams that restart every 8 hours
export YOUTUBE_API_KEY="AIzaSyD..."
export MONITORED_CHANNELS="UC123456789,UC987654321"
```

This will automatically fetch the latest livestreams from these channels when you click "Refresh from YouTube".