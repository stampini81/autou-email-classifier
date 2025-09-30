// Testes E2E Cypress: Classificação de Email - Casos extras

describe('Classificação de Email - Casos Extras', () => {
  beforeEach(() => {
    cy.visit('http://localhost:5001');
    cy.get('textarea[name="emailText"]').clear();
  });

  it('Deve classificar um email improdutivo (felicitação)', () => {
    cy.get('textarea[name="emailText"]').type('Feliz aniversário!');
    cy.get('button[type="submit"]').click();
    cy.wait(500);
    cy.get('#categoria').should('contain.text', 'Improdutivo');
  });

  it('Deve classificar um email improdutivo (agradecimento)', () => {
    cy.get('textarea[name="emailText"]').type('Muito obrigado pelo atendimento.');
  cy.get('button[type="submit"]').click();
  cy.wait(500);
  cy.get('#categoria').should('contain.text', 'Improdutivo');
  });

  it('Deve classificar um email ambíguo como improdutivo', () => {
    cy.get('textarea[name="emailText"]').type('Olá, tudo bem?');
  cy.get('button[type="submit"]').click();
  cy.wait(500);
  cy.get('#categoria').should('contain.text', 'Improdutivo');
  });

  it('Deve classificar um email produtivo (pedido claro)', () => {
    cy.get('textarea[name="emailText"]').type('Solicito atualização do meu cadastro.');
  cy.get('button[type="submit"]').click();
  cy.wait(500);
  cy.get('#categoria').should('contain.text', 'Produtivo');
  });

  it('Deve classificar um email produtivo (pergunta)', () => {
    cy.get('textarea[name="emailText"]').type('Vocês poderiam me enviar o relatório do mês passado?');
  cy.get('button[type="submit"]').click();
  cy.wait(500);
  cy.get('#categoria').should('contain.text', 'Produtivo');
  });
});
