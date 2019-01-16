import React, { Component } from 'react';
import queryString from 'query-string';
import axios from 'axios';

class AuthImplicit extends Component {
  constructor() {
    super();
    this.state = {
      accessToken:"",
      scope:"",
      state:"",
      token_type:"",
      userRef:null,
    };
    this.getUserReference = this.getUserReference.bind(this);
  }

  getUserReference(event) {
    event.preventDefault();

    const options = {
        method: 'GET',
        headers: {'Accept': 'application/vnd.twitchtv.v5+json', 
                  'Client-ID': `${process.env.REACT_APP_TWITCH_CLIENT_ID}`,
                  'Authorization': `OAuth ${this.state.accessToken}`,
        },
        url: 'https://api.twitch.tv/kraken/user'
    };

    axios(options)
    .then((res) => { this.setState({ userRef: res.data }); })
    .catch((err) => { console.log(err); });
  };

  componentDidMount() {
    /** get params from url fragment 
     ** and set them to this.state   **/
    let params = queryString.parse(this.props.location.hash);
    this.setState({
            accessToken: params.access_token,
            scope: params.scope,
            state: params.state,
            token_type: params.token_type
    });
  }

  // the userData list
  get userData() {
    console.log(this.state.userRef);
    return (
        <div>
            <p>_id={this.state.userRef._id}</p>
            <p>bio={this.state.userRef.bio}</p>
            <p>created_at={this.state.userRef.created_at}</p>
            <p>display_name={this.state.userRef.display_name}</p>
            <p>email={this.state.userRef.email}</p>
            <p>email_verified={this.state.userRef.email_verified.toString()}</p>
            <p>logo={this.state.userRef.logo}</p>
            <p>name={this.state.userRef.name}</p>
            <p>notifications.email={this.state.userRef.notifications.email.toString()}</p>
            <p>notifications.push={this.state.userRef.notifications.push.toString()}</p>
            <p>partnered={this.state.userRef.partnered.toString()}</p>
            <p>twitter_connected={this.state.userRef.twitter_connected.toString()}</p>
            <p>type={this.state.userRef.type}</p>
            <p>updated_at={this.state.userRef.updated_at}</p>
        </div>
    );
  }


  render() {
    return (
        <div>
            <p>auth_token={this.state.accessToken}</p>
            <p>scope={this.state.scope}</p>
            <p>state={this.state.state}</p>
            <p>token_type={this.state.token_type}</p>
            {this.state.userRef !== null ? (
              this.userData
            ) : (
              <div>
                  <button onClick={this.getUserReference}>Get user reference</button>
                  <p>There is no user reference.</p>
              </div>
            )}
        </div>

    )
  }
}

export default AuthImplicit;
