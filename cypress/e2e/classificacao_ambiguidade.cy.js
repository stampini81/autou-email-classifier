// Teste Cypress: Ambiguidade entre texto e upload

describe('Classificação de Email - Ambiguidade entre texto e upload', () => {
  it('Deve exibir opção de escolha quando texto e arquivo são enviados', () => {
    cy.visit('http://localhost:5001');
    // Preenche o texto
    cy.get('textarea[name="emailText"]').type('Solicito acesso ao sistema.');
    // Faz upload de arquivo
    cy.get('input[type="file"]').selectFile('teste/Improdutivo.txt', { force: true });
    // Clica em classificar
    cy.get('button[type="submit"]').click();
    // Deve aparecer mensagem de ambiguidade e previews
    cy.contains('Escolha entre texto ou upload para classificação.').should('exist');
    cy.contains('form_preview').should('not.exist'); // preview é só no JSON, não na tela
    cy.contains('file_preview').should('not.exist');
    // Se houver botões para escolher, pode testar aqui
    // cy.get('button').contains('Usar texto').should('exist');
    // cy.get('button').contains('Usar arquivo').should('exist');
  });
});
