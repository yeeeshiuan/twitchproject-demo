import React, { Component } from 'react';
import queryString from 'query-string';
import axios from 'axios';

class AuthImplicit extends Component {
  constructor() {
    super();
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
    .catch((err) => { console.log(err); });
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
    return (
        <div>
            <p>see consoleLog</p>
        </div>

    )
  }
}

export default AuthImplicit;
