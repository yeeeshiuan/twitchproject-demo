import React, { Component } from 'react';
import { Route, Redirect, Switch } from 'react-router-dom';

import App from '../App';

class Logout extends Component {

  componentDidMount() {
    this.props.logoutUser();
  };

  render() {
    return <Switch>
           <Route exact={true} path='/' component={App} />
           <Redirect to='/' />
           </Switch>;
  };
};

export default Logout;
