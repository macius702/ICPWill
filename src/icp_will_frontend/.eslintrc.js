module.exports = {
  extends: [
    // ... twoje inne rozszerzenia
    'plugin:prettier/recommended',
  ],
  plugins: ['prettier'],
  rules: {
    'prettier/prettier': 'error',
    // ... twoje inne reguły
  },
}
