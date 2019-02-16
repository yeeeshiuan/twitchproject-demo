// ***********************************************
// This example commands.js shows you how to
// create various custom commands and overwrite
// existing commands.
//
// For more comprehensive examples of custom
// commands please read more here:
// https://on.cypress.io/custom-commands
// ***********************************************
//
//
// -- This is a parent command --
// Cypress.Commands.add("login", (email, password) => { ... })
//
//
// -- This is a child command --
// Cypress.Commands.add("drag", { prevSubject: 'element'}, (subject, options) => { ... })
//
//
// -- This is a dual command --
// Cypress.Commands.add("dismiss", { prevSubject: 'optional'}, (subject, options) => { ... })
//
//
// -- This is will overwrite an existing command --
// Cypress.Commands.overwrite("visit", (originalFn, url, options) => { ... })

// simulate user login
Cypress.Commands.add('ssoLogin', () => { 
  cy.request({
    method: 'POST',
    url: '/auth/twitchRegister',
    headers: {'Content-Type': 'application/json'},
    body: {
      twitch_id: '9527',
      username: 'joey',
      email:'joey@test.io',
      picture:'http://joey.picture'
    }
  })
  .then((resp) => {
    window.localStorage.setItem('authToken', resp.body.auth_token);
    window.localStorage.setItem('loginType', 'sso');
  })
})




