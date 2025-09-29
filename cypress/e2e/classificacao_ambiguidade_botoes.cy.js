// Teste Cypress: Ambiguidade entre texto e upload, usando ambos os botões

describe('Classificação de Email - Ambiguidade: escolher fonte', () => {
  beforeEach(() => {
    cy.visit('http://localhost:5001');
    cy.get('textarea[name="emailText"]').clear();
    cy.get('input[type="file"]').invoke('val', '');
  });

  it('Deve permitir escolher "Usar Texto" no modal de ambiguidade', () => {
    cy.get('textarea[name="emailText"]').type('Solicito acesso ao sistema.');
    cy.get('input[type="file"]').selectFile('teste/Improdutivo.txt', { force: true });
    cy.get('button[type="submit"]').click();
    cy.contains('Escolha a fonte para classificação').should('be.visible');
    cy.get('#useFormBtn').click();
    cy.get('#categoria').should('contain.text', 'Produtivo');
  });

  it('Deve permitir escolher "Usar Upload" no modal de ambiguidade', () => {
    cy.get('textarea[name="emailText"]').type('Solicito acesso ao sistema.');
    cy.get('input[type="file"]').selectFile('teste/Improdutivo.txt', { force: true });
    cy.get('button[type="submit"]').click();
    cy.contains('Escolha a fonte para classificação').should('be.visible');
    cy.get('#useFileBtn').click();
    cy.get('#categoria').should('contain.text', 'Improdutivo');
  });
});
