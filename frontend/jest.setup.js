const AllureReporter = require('jest-allure/dist/setup-allure');

module.exports = {
  setupFilesAfterEnv: ['jest-allure/dist/setup-allure'],
};
