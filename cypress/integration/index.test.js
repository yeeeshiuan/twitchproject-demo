const username = "joey777";
const display_name = "煞氣的Joey";
const keyword = "工程師";
const sentence = "工程師是你？";
const channelName = "頻道ID";
const countTag = "筆數： 1";


describe('Index', () => {

  it('should display the page correctly if a user is not logged in', () => {
    cy
      .visit('/')
      .get('label').contains(channelName)
      .get('.navbar-burger').click()
      .get('a').contains('About')
      .get('a').contains('Log In By Twitch');
  });

  it('should display and act the page correctly if a user logined', () => {
    cy.ssoLogin()
      .visit('/')
      .get('label').contains(channelName)
      .get('.navbar-burger').click()
      .get('a').contains('About')
      .get('a').contains('Log Out Here!');

    cy.server();
    cy.route('POST', '/repository/findSentencesByUsername/' + username).as('findSentencesByUsername');
    cy.get('input[name="findSentencesByUsername"]').type(username)
      .get('input[data-cy="usernameSubmit"]').click()
      .wait('@findSentencesByUsername')
      .wait(500)
      .get('.searchPanel > div > ul > li').should('have.length', 2)
      .first().contains(countTag)
      .get('.searchPanel > div > ul > li')
      .eq(1).should('contain', sentence);

    cy.server();
    cy.route('POST', '/repository/findSentencesByDisplayname/' + display_name).as('findSentencesByDisplay_name');
    cy.get('input[name="findSentencesByDisplay_name"]').type(display_name)
      .get('input[data-cy="display_nameSubmit"]').click()
      .wait('@findSentencesByDisplay_name')
      .wait(500)
      .get('.searchPanel > div > ul > li').should('have.length', 2)
      .first().contains(countTag)
      .get('.searchPanel > div > ul > li')
      .eq(1).should('contain', sentence);

    cy.server();
    cy.route('POST', '/repository/findDisplaynamesByKeyword/' + keyword).as('findDisplay_namesByKeyword');
    cy.get('input[name="findDisplay_namesByKeyword"]').type(keyword)
      .get('input[data-cy="keywordSubmit"]').click()
      .wait('@findDisplay_namesByKeyword')
      .wait(500)
      .get('.searchPanel > div > ul > li').should('have.length', 2)
      .first().contains(countTag)
      .get('.searchPanel > div > ul > li')
      .eq(1).should('contain', display_name);

    cy.server();
    cy.route('POST', '/repository/findDisplaynamesBySentence/' + sentence).as('findDisplay_namesBySentence');
    cy.get('input[name="findDisplay_namesBySentence"]').type(sentence)
      .get('input[data-cy="sentenceSubmit"]').click()
      .wait('@findDisplay_namesBySentence')
      .wait(500)
      .get('.searchPanel > div > ul > li').should('have.length', 2)
      .first().contains(countTag)
      .get('.searchPanel > div > ul > li')
      .eq(1).should('contain', display_name);

  });

  it('after login test, should display the page correctly if a user is not logged in', () => {
    cy
      .visit('/')
      .get('label').contains(channelName)
      .get('.navbar-burger').click()
      .get('a').contains('About')
      .get('a').contains('Log In By Twitch');
  });
});

