import React, { Component } from 'react';
import ReactTwitchEmbedVideo from 'react-twitch-embed-video';
import TwitchIRC from './components/TwitchIRC';

class App extends Component {
  constructor() {
    super();
    this.state = {
      twitchEmbedVideoProps:{
        /** Optional for VOD embeds; otherwise, required. 
            Name of the chat room and channel to stream. */
        channel: `${process.env.REACT_APP_TWITCH_CHANNEL_NAME}`,
        /** Width of video embed including chat */
        width: "940",
        /** Maximum width of the rendered element, in pixels. 
            This can be expressed as a percentage, by passing a string like 100% */
        height: "480",
        /** If true, the player can go full screen. Default: true. */
        allowfullscreen: false,
        /** Determines the screen layout. Valid values:
            video-and-chat: Default if channel is provided. Shows both video and chat side-by-side. 
              At narrow sizes, chat renders under the video player.
          * video: Default if channel is not provided. Shows only the video player (omits chat). */
        layout: "video-with-chat",
        /** The Twitch embed color theme to use. Valid values: light or dark. Default: light. */
        theme: "dark",
      },
    };
  };

  componentDidMount() {
    this.updateChannelName("kyo1984123");
  };

  updateChannelName(channelName) {
    // update channel
    this.setState({
      twitchEmbedVideoProps:{
        channel:channelName,
      },
    });
  };

  render() {
    return (
      <div className="App">
        <header className="App-header">
          <div>
            <p>
              Hello world!
            </p>
          </div>
          <TwitchIRC />
          <div>
            <ReactTwitchEmbedVideo {...this.state.twitchEmbedVideoProps} />
          </div>
        </header>
      </div>
    );
  }
}

export default App;
