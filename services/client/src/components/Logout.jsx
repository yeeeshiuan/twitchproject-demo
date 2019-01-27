import React, { Component } from 'react';

class Logout extends Component {

  componentDidMount() {
    this.props.logoutUser();
  };

  render() {
    return (
      <div>
        <p>你已經登出。</p>
      </div>
    )
  };
};

export default Logout;
