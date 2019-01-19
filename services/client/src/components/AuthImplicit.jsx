import React, { Component } from 'react';
import { Redirect } from 'react-router-dom';

import queryString from 'query-string';
import axios from 'axios';

class AuthImplicit extends Component {
  constructor() {
    super();
    this.state = {
        twitchUnauthorized: false,
    };
  }

  getUserReference(token) {
    const options = {
        method: 'GET',
        headers: {'Accept': 'application/vnd.twitchtv.v5+json', 
                  'Client-ID': `${process.env.REACT_APP_TWITCH_CLIENT_ID}`,
                  'Authorization': `OAuth ${token}`,
        },
        url: 'https://api.twitch.tv/kraken/user'
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
            
            // user doesn't give twitch the authoried
            if (error.response.data.error === "Unauthorized") {
                this.setState({twitchUnauthorized: true});
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
        url: `${process.env.REACT_APP_USERS_SERVICE_URL}/auth/twitchRegister`
    };

    console.log(options);

    axios(options)
    .then((res) => { 
        console.log(res.data);
        this.props.loginUser(res.data.auth_token);
    })
    .catch((err) => { console.log(err); });
  }

  componentDidMount() {
    /** get params from url fragment **/
    let params = queryString.parse(this.props.location.hash);
    this.getUserReference(params.access_token);
  }

  render() {
    if (this.state.twitchUnauthorized) {
      return <Redirect to='/' />;
    };
    return (
        <div>
            <p>see consoleLog</p>
        </div>

    )
  }
}

export default AuthImplicit;
