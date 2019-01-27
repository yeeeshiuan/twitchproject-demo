import React, { Component } from 'react';
import { Route, Switch } from 'react-router-dom';

import TwitchIRC from './components/TwitchIRC';
import TwitchEmbedVideo from './components/TwitchEmbedVideo';
import AuthImplicit from './components/AuthImplicit';
import NavBar from './components/NavBar';
import Logout from './components/Logout';
import Footer from './components/Footer';

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
      title: 'TwitchProjectDemo',
      channelName:`${process.env.REACT_APP_TWITCH_CHANNEL_NAME}`,
      twitchOAuthImplicit:`${process.env.REACT_APP_TWITCH_OAUTH_LINK}?client_id=${process.env.REACT_APP_TWITCH_CLIENT_ID}&redirect_uri=${process.env.REACT_APP_TWITCH_CALLBACK_URL}&response_type=token&scope=user_read&state=${process.env.REACT_APP_CSRF_TOKEN}`,
      isAuthenticated: false,
      // normal: register by this site
      // sso   : login by twitch or google SSO
      loginType: "normal",
      enableLexicalAnalyzeService: true,
    };
    /** event binding **/
    this.changeChannel = this.changeChannel.bind(this);
    this.handleChangeChannel = this.handleChangeChannel.bind(this);
    this.loginUser = this.loginUser.bind(this);
    this.logoutUser = this.logoutUser.bind(this);
  };

  componentDidMount() {
    
  }

  componentWillMount() {
    if (window.localStorage.getItem('authToken')) {
      this.setState({ isAuthenticated: true,
                      loginType: window.localStorage.getItem('authToken')
      });
    };
  };

  loginUser(token, loginType) {
    window.localStorage.setItem('authToken', token);
    window.localStorage.setItem('loginType', loginType);
    this.setState({ isAuthenticated: true,
                    loginType: loginType
    });
  };

  logoutUser() {
    window.localStorage.clear();
    this.setState({ isAuthenticated: false });
  };

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
      <div>
        <NavBar
          title={this.state.title}
          isAuthenticated={this.state.isAuthenticated}
          twitchOAuthImplicit={this.state.twitchOAuthImplicit}
        />
        <div>
            <TwitchEmbedVideo {...this.state.twitchEmbedVideoProps} />
        </div>
        <div>
          <form onSubmit={(event) => this.changeChannel(event)}>
            <input
              name="channelName"
              className="input is-large"
              type="text"
              placeholder="Enter channel name"
              value={this.state.channelName}
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
          { this.loginTwitchButton }
          { this.lexicalAuthTest }
        <div>
          <TwitchIRC twitchIRCProps={this.state.twitchIRCProps} 
                       isAuthenticated={this.state.isAuthenticated}
                       enableLexicalAnalyzeService={this.state.enableLexicalAnalyzeService}
          />
        </div>
        <Switch>
            <Route path="/authByTwitch" render={(props) => (
              <AuthImplicit 
                  loginUser={this.loginUser}
                  {...props} 
              />
            )} />
            <Route exact path='/logout' render={() => (
              <Logout
                logoutUser={this.logoutUser}
                isAuthenticated={this.state.isAuthenticated}
              />
            )} />
        </Switch>
        <Footer />
      </div>
    );
  }
}

export default App;
