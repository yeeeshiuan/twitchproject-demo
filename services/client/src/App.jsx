import React, { Component } from 'react';
import { Route, Switch } from 'react-router-dom';

import NavBar from './components/NavBar';
import Message from './components/Message';
import Main from './components/Main';
import AuthImplicit from './components/AuthImplicit';
import Logout from './components/Logout';
import Footer from './components/Footer';

class App extends Component {
  constructor() {
    super();
    this.state = {
      title: "TwitchprojectDemo",
      messageName: null,
      messageType: null,
      isAuthenticated: false,
      // normal: register by this site (not yet)
      // sso   : login by twitch or google SSO
      loginType: "normal",
      enableLexicalAnalyzeService: true, // TODO
      enableRepository: true, // TODO
      twitchOAuthImplicit:`${process.env.REACT_APP_TWITCH_OAUTH_LINK}?client_id=${process.env.REACT_APP_TWITCH_CLIENT_ID}&redirect_uri=${process.env.REACT_APP_TWITCH_CALLBACK_URL}&response_type=token&scope=user_read&state=${process.env.REACT_APP_CSRF_TOKEN}`,
    };
    this.loginUser = this.loginUser.bind(this);
    this.logoutUser = this.logoutUser.bind(this);
    this.createMessage = this.createMessage.bind(this);
    this.removeMessage = this.removeMessage.bind(this);
  }

  componentWillMount() {
    if (window.localStorage.getItem('authToken')) {
      this.setState({ isAuthenticated: true,
                      loginType: window.localStorage.getItem('loginType')
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
    this.createMessage('你已經登出！','success');
  };

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
        <Switch>
            <Route exact path="/" render={() => (
              <Main isAuthenticated={this.state.isAuthenticated}
                    createMessage={this.createMessage}
                    enableRepository={this.state.enableRepository}
                    enableLexicalAnalyzeService={this.state.enableLexicalAnalyzeService} />
            )} />
            <Route exact path="/authByTwitch" render={(props) => (
              <AuthImplicit 
                  loginUser={this.loginUser}
                  enableRepository={this.state.enableRepository}
                  {...props} 
              />
            )} />
            <Route exact path='/logout' render={() => (
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
