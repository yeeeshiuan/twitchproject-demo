import React, { Component } from 'react';
import { Route, Redirect, Switch } from 'react-router-dom';

import qs from 'query-string';
import axios from 'axios';

import App from '../App';

class AuthImplicit extends Component {
  constructor() {
    super();
    this.state = {
        twitchUnauthorized: false,
    };
  }

  componentDidMount() {
    /** get params from url fragment **/
    let params = qs.parse(this.props.location.hash);
    this.getUserReference(params.access_token, params.state);
  }

  getUserReference(token, state) {

    // CSRF isn't correct
    if (state !== `${process.env.REACT_APP_CSRF_TOKEN}`) {
        this.setState({twitchUnauthorized: true});
        return;
    }

    const options = {
        method: 'GET',
        headers: {'Accept': 'application/vnd.twitchtv.v5+json', //TODO
                  'Client-ID': `${process.env.REACT_APP_TWITCH_CLIENT_ID}`,
                  'Authorization': `OAuth ${token}`,
        },
        url: 'https://api.twitch.tv/kraken/user' //TODO
    };

    axios(options)
    .then((res) => { 
        this.registerUserByTwitchRef(res.data); 
    })
  }

  registerUserByTwitchRef(userRef) {

    const options = {
        method: 'POST',
        data: {
            twitch_id: userRef._id,
            username: userRef.display_name,
            email: userRef.email,
            picture: userRef.logo
        },
        url: `${process.env.REACT_APP_DOMAIN_NAME_URL}/auth/twitchRegister`
    };

    axios(options)
    .then((res) => { 
        this.props.loginUser(res.data.auth_token, "sso");
        if (this.props.enableRepository && res.data.message === "Successfully registered.") {
            this.createDatabaseForThisUser();
        }
    })
  }

  createDatabaseForThisUser() {
    const options = {
        method: 'POST',
        headers: {'Content-Type': 'application/json',
                  'Authorization': `Bearer ${window.localStorage.authToken}`,
                  'LoginType': `${window.localStorage.loginType}`,
        },
        url: `${process.env.REACT_APP_DOMAIN_NAME_URL}/repository/createuser`
    };

    axios(options)
    .then((res) => { 
    })
  }

  render() {
    return <Switch>
           <Route exact={true} path='/' component={App} />
           <Redirect to='/' />
           </Switch>;
  }
}

export default AuthImplicit;
