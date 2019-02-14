import React, { Component } from 'react';
import { Route, Switch } from 'react-router-dom';
import axios from 'axios';

import TwitchIRC from './components/TwitchIRC';
import TwitchEmbedVideo from './components/TwitchEmbedVideo';
import AuthImplicit from './components/AuthImplicit';
import NavBar from './components/NavBar';
import Logout from './components/Logout';
import Footer from './components/Footer';
import MessageList from './components/MessageList';
import Message from './components/Message';

import './style.css';

class App extends Component {
  constructor() {
    super();
    this.state = {
      twitchEmbedVideoProps:{
        /** Optional for VOD embeds; otherwise, required. 
            Name of the chat room and channel to stream. */
        channel: "",
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
        channels: [],
      },
      title: 'TwitchProjectDemo',
      channelName: "",
      twitchOAuthImplicit:`${process.env.REACT_APP_TWITCH_OAUTH_LINK}?client_id=${process.env.REACT_APP_TWITCH_CLIENT_ID}&redirect_uri=${process.env.REACT_APP_TWITCH_CALLBACK_URL}&response_type=token&scope=user_read&state=${process.env.REACT_APP_CSRF_TOKEN}`,
      isAuthenticated: false,
      // normal: register by this site (not yet)
      // sso   : login by twitch or google SSO
      loginType: "normal",
      enableLexicalAnalyzeService: true, // TODO
      enableRepository: true, // TODO
      // nouns, adjs, verbs
      chartDataSelect: "nouns",
      resetChartData: false,
      findSentencesByUsername: "",
      findSentencesByDisplay_name: "",
      findDisplay_namesByKeyword: "",
      findDisplay_namesBySentence: "",
      findingResult: [],
      messageName: null,
      messageType: null,
    };
    /** event binding **/
    this.changeChannel = this.changeChannel.bind(this);
    this.handleChangeEvent = this.handleChangeEvent.bind(this);
    this.loginUser = this.loginUser.bind(this);
    this.logoutUser = this.logoutUser.bind(this);
    this.changeChartDataSelect = this.changeChartDataSelect.bind(this);
    this.resetChartData = this.resetChartData.bind(this);
    this.updateRoomID = this.updateRoomID.bind(this);

    this.createMessage = this.createMessage.bind(this);
    this.removeMessage = this.removeMessage.bind(this);

    this.findSentencesByUsername = this.findSentencesByUsername.bind(this);
    this.findSentencesByDisplay_name = this.findSentencesByDisplay_name.bind(this);
    this.findDisplay_namesByKeyword = this.findDisplay_namesByKeyword.bind(this);
    this.findDisplay_namesBySentence = this.findDisplay_namesBySentence.bind(this);
  };

  componentWillMount() {
    if (window.localStorage.getItem('authToken')) {
      this.setState({ isAuthenticated: true,
                      loginType: window.localStorage.getItem('authToken')
      });
    };
  };

  componentDidMount() {
    // if there is no channel name there, get the top stream channel
    if (!window.localStorage.getItem('channelName')) {
        this.getTopStreamName();
    } else {
        let channelName = window.localStorage.getItem('channelName');
        this.updateChannelName(channelName);
    }
  }

  getTopStreamName() {

    const options = {
        method: 'GET',
        headers: {'Accept': 'application/vnd.twitchtv.v5+json', //TODO
                  'Client-ID': `${process.env.REACT_APP_TWITCH_CLIENT_ID}`,
        },
        url: `${process.env.REACT_APP_TWITCH_TOP_STREAM_API_URL}`
    };

    axios(options)
    .then((res) => { 
        let channelName = res.data.streams[0].channel.name;
        this.updateChannelName(channelName);
        window.localStorage.setItem('channelName', channelName);
    })
    .catch((error) => { 
        // Error
        if (error.response) {
            // The request was made and the server responded with a status code
            // that falls out of the range of 2xx
            console.log(error.response.data);
            console.log(error.response.status);
            console.log(error.response.headers);
            
            // user doesn't give twitch the auth
            if (error.response.data.error === "Unauthorized") {
                this.setState({twitchUnauthorized: true});
                console.log("Twitch return error.(Unauthorized)");
            }
            
        } else if (error.request) {
            // The request was made but no response was received
            // `error.request` is an instance of XMLHttpRequest in the browser and an instance of
            // http.ClientRequest in node.js
            console.log(error.request);
        } else {
            // Something happened in setting up the request that triggered an Error
            console.log('Error', error.message);
        }
        console.log(error.config);
     });
  }

  repositoryFindRequest(partURI) {
    const options = {
        method: 'POST',
        headers: {'Content-Type': 'application/json',
                  'Authorization': `Bearer ${window.localStorage.authToken}`,
                  'LoginType': `${window.localStorage.loginType}`,
        },
        url: `${process.env.REACT_APP_DOMAIN_NAME_URL}/repository${partURI}`,
    };

    axios(options)
    .then((res) => { 
        console.log(res.data);
        this.setState({findingResult: res.data.message});
    })
    .catch((error) => { 
        // Error
        if (error.response) {
            // The request was made and the server responded with a status code
            // that falls out of the range of 2xx
            console.log(error.response.data);
            console.log(error.response.status);
            console.log(error.response.headers);
            
            // user doesn't give twitch the auth
            if (error.response.data.error === "Unauthorized") {
                this.setState({twitchUnauthorized: true});
                console.log("Twitch return error.(Unauthorized)");
            }
            
        } else if (error.request) {
            // The request was made but no response was received
            // `error.request` is an instance of XMLHttpRequest in the browser and an instance of
            // http.ClientRequest in node.js
            console.log(error.request);
        } else {
            // Something happened in setting up the request that triggered an Error
            console.log('Error', error.message);
        }
        console.log(error.config);
        this.setState({findingResult: []});
     });
  }

  updateRoomID(roomId) {
    const options = {
        method: 'GET',
        headers: {'Accept': 'application/vnd.twitchtv.v5+json', //TODO
                  'Client-ID': `${process.env.REACT_APP_TWITCH_CLIENT_ID}`,
        },
        url: 'https://api.twitch.tv/kraken/channels/' + roomId //TODO
    };

    axios(options)
    .then((res) => { 
        let channelName = res.data.status;
        window.localStorage.setItem(roomId, channelName);
    })
    .catch((error) => { 
        // Error
        if (error.response) {
            // The request was made and the server responded with a status code
            // that falls out of the range of 2xx
            console.log(error.response.data);
            console.log(error.response.status);
            console.log(error.response.headers);
            
            // user doesn't give twitch the auth
            if (error.response.data.error === "Unauthorized") {
                this.setState({twitchUnauthorized: true});
                console.log("Twitch return error.(Unauthorized)");
            }
            
        } else if (error.request) {
            // The request was made but no response was received
            // `error.request` is an instance of XMLHttpRequest in the browser and an instance of
            // http.ClientRequest in node.js
            console.log(error.request);
        } else {
            // Something happened in setting up the request that triggered an Error
            console.log('Error', error.message);
        }
        console.log(error.config);
     });
  }

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
    this.createMessage('你已經登出！','success');
  };

  updateChannelName(channelName) {
    let twitchIRCProps = this.state.twitchIRCProps;
    if ( twitchIRCProps.channels.length ) {
        twitchIRCProps.channels.pop();
    }
    twitchIRCProps.channels.push(channelName);

    let twitchEmbedVideoProps = this.state.twitchEmbedVideoProps;
    twitchEmbedVideoProps.channel = channelName;

    this.setState({channelName: channelName,
                   twitchIRCProps: twitchIRCProps,
                   twitchEmbedVideoProps:twitchEmbedVideoProps,
    });

    window.localStorage.setItem('channelName', channelName);
  }

  changeChannel(event) {
    event.preventDefault();
    this.updateChannelName(this.state.channelName);
  }

  handleChangeEvent(event) {
    const obj = {};
    obj[event.target.name] = event.target.value;
    this.setState(obj);
  }

  findSentencesByUsername(event) {
    event.preventDefault();
    let partURI = "/findSentencesByUsername/" + this.state.findSentencesByUsername;
    this.repositoryFindRequest(partURI);
  }

  findSentencesByDisplay_name(event) {
    event.preventDefault();
    let partURI = "/findSentencesByDisplayname/" + this.state.findSentencesByDisplay_name;
    this.repositoryFindRequest(partURI);
  }

  findDisplay_namesByKeyword(event) {
    event.preventDefault();
    let partURI = "/findDisplaynamesByKeyword/" + this.state.findDisplay_namesByKeyword;
    this.repositoryFindRequest(partURI);
  }

  findDisplay_namesBySentence(event) {
    event.preventDefault();
    let partURI = "/findDisplaynamesBySentence/" + this.state.findDisplay_namesBySentence;
    this.repositoryFindRequest(partURI);

  }

  changeChartDataSelect(event) {
    const obj = {};
    obj[event.target.name] = event.target.value;
    this.setState(obj);
  }

  resetChartData(event) {
    this.setState({resetChartData: !this.state.resetChartData});
  }

  createMessage(name='Sanity Check', type='success') {
    this.setState({
      messageName: name,
      messageType: type
    });

    setTimeout(() => {
      this.removeMessage();
    }, 3000);
  };

  removeMessage() {
    this.setState({
      messageName: null,
      messageType: null
    });
  };

  render() {
    // if request not response, don't rendering
    if (!this.state.twitchIRCProps.channels.length) {
        return null;
    }
    return (
      <div>
        <NavBar
          title={this.state.title}
          isAuthenticated={this.state.isAuthenticated}
          twitchOAuthImplicit={this.state.twitchOAuthImplicit}
        />
       {this.state.messageName && this.state.messageType &&
         <Message
           messageName={this.state.messageName}
           messageType={this.state.messageType}
           removeMessage={this.removeMessage}
         />
       }
        <div className="controlPanel">
          <form onSubmit={(event) => this.changeChannel(event)}>
            <div className="field">
                <label className="label">頻道ID</label>
            </div>
            <div className="field has-addons">
                <div className="control">
                    <input
                      name="channelName"
                      className="input"
                      type="text"
                      placeholder="請輸入頻道ID"
                      value={this.state.channelName}
                      required
                      onChange={this.handleChangeEvent}
                    />
                </div>
                <div className="control">
                    <input
                      type="submit"
                      className="button is-info"
                      value="換頻道"
                    />
                </div>
            </div>
          </form>
          { this.state.isAuthenticated &&
            <div onChange={this.changeChartDataSelect}>
                <div className="field">
                    <label className="label">圖表資料類型(每十筆留言才會做一次分詞服務[採用
                        <a href="https://github.com/fxsjy/jieba" target="_blank" rel="noopener noreferrer">jieba</a>])
                    </label>
                </div>
                <div className="control">
                  <label className="radio">
                    <input type="radio" name="chartDataSelect" value="nouns" defaultChecked />
                    名詞
                  </label>
                  <label className="radio">
                    <input type="radio" name="chartDataSelect" value="verbs"  />
                    動詞
                  </label>
                  <label className="radio">
                    <input type="radio" name="chartDataSelect" value="adjs"  />
                    形容詞
                  </label>
                </div>
            </div>
          }
          { this.state.isAuthenticated &&
          <div className="control">
            <div className="field">
                <label className="label">重置BarChart的data</label>
            </div>
            <button className="button is-danger is-small"
                    onClick={this.resetChartData} 
            >重置
            </button>
          </div>
          }
          { this.state.isAuthenticated &&
          <form onSubmit={(event) => this.findSentencesByUsername(event)}>
            <div className="field">
                <label className="label">用ID找發言</label>
            </div>
            <div className="field has-addons">
                <div className="control">
                    <input
                      name="findSentencesByUsername"
                      className="input"
                      type="text"
                      placeholder="請輸入留言者ID"
                      value={this.state.findSentencesByUsername}
                      required
                      onChange={this.handleChangeEvent}
                    />
                </div>
                <div className="control">
                    <input
                      type="submit"
                      className="button is-info"
                      value="尋找"
                    />
                </div>
            </div>
          </form>
          }
          { this.state.isAuthenticated &&
          <form onSubmit={(event) => this.findSentencesByDisplay_name(event)}>
            <div className="field">
                <label className="label">用名稱找發言</label>
            </div>
            <div className="field has-addons">
                <div className="control">
                    <input
                      name="findSentencesByDisplay_name"
                      className="input"
                      type="text"
                      placeholder="請輸入留言者名稱"
                      value={this.state.findSentencesByDisplay_name}
                      required
                      onChange={this.handleChangeEvent}
                    />
                </div>
                <div className="control">
                    <input
                      type="submit"
                      className="button is-info"
                      value="尋找"
                    />
                </div>
            </div>
          </form>
          }
          { this.state.isAuthenticated &&
          <form onSubmit={(event) => this.findDisplay_namesByKeyword(event)}>
            <div className="field">
                <label className="label">用分詞找發言人名稱</label>
            </div>
            <div className="field has-addons">
                <div className="control">
                    <input
                      name="findDisplay_namesByKeyword"
                      className="input"
                      type="text"
                      placeholder="請輸入分詞"
                      value={this.state.findDisplay_namesByKeyword}
                      required
                      onChange={this.handleChangeEvent}
                    />
                </div>
                <div className="control">
                    <input
                      type="submit"
                      className="button is-info"
                      value="尋找"
                    />
                </div>
            </div>
          </form>
          }
          { this.state.isAuthenticated &&
          <form onSubmit={(event) => this.findDisplay_namesBySentence(event)}>
            <div className="field">
                <label className="label">用完整的句子找發言人名稱</label>
            </div>
            <div className="field has-addons">
                <div className="control">
                    <input
                      name="findDisplay_namesBySentence"
                      className="input"
                      type="text"
                      placeholder="請輸入完整的句子"
                      value={this.state.findDisplay_namesBySentence}
                      required
                      onChange={this.handleChangeEvent}
                    />
                </div>
                <div className="control">
                    <input
                      type="submit"
                      className="button is-info"
                      value="尋找"
                    />
                </div>
            </div>
          </form>
          }
        </div>
        <div className="flowLeft">
            <TwitchEmbedVideo {...this.state.twitchEmbedVideoProps} />
        </div>
        <div className="chartPanel">
          <TwitchIRC twitchIRCProps={this.state.twitchIRCProps} 
                     isAuthenticated={this.state.isAuthenticated}
                     enableLexicalAnalyzeService={this.state.enableLexicalAnalyzeService}
                     enableRepository={this.state.enableRepository}
                     chartDataSelect={this.state.chartDataSelect}
                     resetChartData={this.state.resetChartData}
                     updateRoomID={this.updateRoomID}
          />
        </div>
        <div className="searchPanel">
            <MessageList findingResult={this.state.findingResult} />
        </div>
        <Switch>
            <Route path="/authByTwitch" render={(props) => (
              <AuthImplicit 
                  loginUser={this.loginUser}
                  enableRepository={this.state.enableRepository}
                  {...props} 
              />
            )} />
            <Route path='/logout' render={() => (
              <Logout
                logoutUser={this.logoutUser}
              />
            )} />
        </Switch>
        <Footer className="footerPanel" />
      </div>
    )
  }
};

export default App;
