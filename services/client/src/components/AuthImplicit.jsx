import React, { Component } from 'react';
import { Redirect } from 'react-router-dom';

import qs from 'query-string';
import axios from 'axios';

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
        console.log("CSRF is not correct.");
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
        console.log(res.data);
        this.registerUserByTwitchRef(res.data); 
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
        console.log(res.data);
        this.props.loginUser(res.data.auth_token, "sso");
        if (this.props.enableRepository && res.data.message === "Successfully registered.") {
            this.createDatabaseForThisUser();
        }
    })
    .catch((err) => { console.log(err); });
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
        console.log(res.data);
    })
    .catch((err) => { console.log(err); });
  }

  render() {
    return <Redirect to='/' />;
  }
}

export default AuthImplicit;
