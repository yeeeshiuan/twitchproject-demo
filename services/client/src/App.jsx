import React, { Component } from 'react';
import axios from 'axios';
import { Route, Switch } from 'react-router-dom';

import TwitchIRC from './components/TwitchIRC';
import TwitchEmbedVideo from './components/TwitchEmbedVideo';
import AuthImplicit from './components/AuthImplicit';

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
      twitchIRCProps: {
        options: {
        /** delieve log messages */
            debug: false
        },
        connection: {
            reconnect: true
        },
        identity: {
          username:`${process.env.REACT_APP_TWITCH_USER_NAME}` ,
          password:`${process.env.REACT_APP_TWITCH_OAUTH_TOKEN}`,
        },
        channels: [
          `${process.env.REACT_APP_TWITCH_CHANNEL_NAME}`,
        ],
      },
      channelName:"",
      twitchOAuthImplicit:`${process.env.REACT_APP_TWITCH_OAUTH_LINK}?client_id=${process.env.REACT_APP_TWITCH_CLIENT_ID}&redirect_uri=${process.env.REACT_APP_DOMAIN_NAME}&response_type=token&scope=viewing_activity_read&state=${process.env.REACT_APP_CSRF_TOKEN}`,
    };
    /** event binding **/
    this.changeChannel = this.changeChannel.bind(this);
    this.handleChangeChannel = this.handleChangeChannel.bind(this);
  };

  componentDidMount() {
    
  }

  updateChannelName(channelName) {
    // update channel
    const obj = this.state;
    obj.twitchEmbedVideoProps.channel = channelName;
    // remove old channel
    obj.twitchIRCProps.channels.pop();
    // add new channel
    obj.twitchIRCProps.channels.push(channelName);
    // update
    this.setState({...obj});
  }

  changeChannel(event) {
    event.preventDefault();
    this.updateChannelName(this.state.channelName);
  }

  handleChangeChannel(event) {
    const obj = {};
    obj[event.target.name] = event.target.value;
    this.setState(obj);
  }

  render() {
    return (
      <div className="App">
        <header className="App-header">
          <div>
            <p>
              Hello world!
            </p>
          </div>
          <div>
            <TwitchIRC twitchIRCProps={this.state.twitchIRCProps}/>
          </div>
          <div>
            <form onSubmit={(event) => this.changeChannel(event)}>
              <input
                name="channelName"
                className="input is-large"
                type="text"
                placeholder="Enter channel name"
                required
                onChange={this.handleChangeChannel}
              />
              <input
                type="submit"
                className="button is-primary is-large is-fullwidth"
                value="Submit"
              />
            </form>
          </div>
          <div>
            <TwitchEmbedVideo {...this.state.twitchEmbedVideoProps} />
          </div>
          <div>
            <a href={this.state.twitchOAuthImplicit}>login twitch</a>
          </div>
          <Switch>
              <Route path="/auth" render={(props) => (
                <AuthImplicit {...props} />
              )} />
          </Switch>
        </header>
      </div>
    );
  }
}

export default App;
