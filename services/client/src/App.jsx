import React, { Component } from 'react';

class App extends Component {
  constructor() {
    super();
    this.state = {
      mongodb:"123",
    };
  };

  render() {
    return (
      <div className="App">
        <header className="App-header">
          <p>
            Hello world!
          </p>
        </header>
      </div>
    );
  }
}

export default App;
