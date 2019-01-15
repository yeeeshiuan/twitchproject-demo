import React, { Component } from 'react';
import queryString from 'query-string';

class AuthImplicit extends Component {
  constructor() {
    super();
    this.state = {
      accessToken:"",
      scope:"",
      state:"",
      token_type:"",
    };
  }

  componentDidMount() {
    let params = queryString.parse(this.props.location.hash);
    this.setState({
            accessToken: params.access_token,
            scope: params.scope,
            state: params.state,
            token_type: params.token_type
    });
  }


  render() {
    return (
        <div>
            <p>auth_token={this.state.accessToken}</p>
            <p>scope={this.state.scope}</p>
            <p>state={this.state.state}</p>
            <p>token_type={this.state.token_type}</p>
        </div>
    )
  }
}

export default AuthImplicit;
