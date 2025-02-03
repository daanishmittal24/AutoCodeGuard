module.exports = {
  "env": {
      "browser": true,
      "node": true
  },
  "extends": [
      "eslint:recommended"
  ],
  "rules": {
      // Enforce camelCase naming convention
      "camelcase": ["error", { "properties": "always" }],
      
      // Ensure semicolons are always used
      "semi": ["error", "always"],
      
      // No unused variables
      "no-unused-vars": ["error"],
      
      // No console.log usage
      "no-console": ["error"],
      
      // Enforce strict equality
      "eqeqeq": ["error", "always"],
      
      // Disallow undefined variables
      "no-undef": ["error"],
      
      // Require function names to be in camelCase
      "func-names": ["error", "always"],
      
      // Ensure that variables are defined before being used
      "no-use-before-define": ["error"],
      
      // Force a specific indentation style (2 spaces)
      "indent": ["error", 2],

      // No trailing spaces at the end of lines
      "no-trailing-spaces": "error",
      
      // Warn about empty block statements
      "no-empty": "warn"
  }
};
