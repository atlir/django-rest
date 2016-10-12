'use strict';

// Define the `phonecatApp` module
angular.module('gmailApp', [
    'ngRoute',
    'LocalStorageModule',
    'ngAnimate',
    'ui.bootstrap'
])
    .config(['$httpProvider', function($httpProvider) {
        $httpProvider.defaults.xsrfCookieName = 'csrftoken';
        $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
    }])
