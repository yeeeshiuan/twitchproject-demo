import React, { Component } from 'react';
import { Route, Redirect, Switch } from 'react-router-dom';
import axios from 'axios';

import App from '../App';

class Logout extends Component {

  componentDidMount() {
    this.logoutUserFromBackEnd();
    this.props.logoutUser();
  };

  logoutUserFromBackEnd() {
    const options = {
        method: 'GET',
        headers: {'Content-Type': 'application/json',
                  'Authorization': `Bearer ${window.localStorage.authToken}`,
                  'LoginType': `${window.localStorage.loginType}`,
        },
        url: `${process.env.REACT_APP_DOMAIN_NAME_URL}/auth/logout`
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
  };
};

export default Logout;
