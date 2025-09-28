// Teste E2E Cypress: Classificação de Email

describe('Classificação de Email', () => {
  it('Deve classificar um email produtivo', () => {
  cy.visit('http://localhost:5001');
    cy.get('textarea[name="emailText"]').type('Solicito acesso ao sistema.');
    cy.get('button[type="submit"]').click();
    cy.contains('Categoria').should('exist');
    cy.contains('Produtivo').should('exist');
  });
});
