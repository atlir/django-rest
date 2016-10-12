'use strict';

var appComponent = {
    templateUrl: 'static/js/templates/template.html',
    controller: ['$scope', 'Auth', 'Threads',
        function($scope, Auth, Threads) {
            this.showUser = this.loaded = this.nextPageToken = false;
            this.threads = [];
            this.prevPageTokens = [];
            $scope.user = false;

            Auth.isAuthenticated().then((data) => {
                if (data.user) {
                    this.showUser = true;
                    $scope.user = data.user;
                } else {
                    this.showUser = false;
                    this.user = false;
                }
            }).catch((error) => {
                console.log('Error: ', error);
            });

            this.login = function() {
                Auth.login().then((data) => {
                    this.showUser = true;
                    $scope.user = data.user;
                }).catch((error) => {
                    console.log('Error: ', error);
                });
            };

            this.logout = function() {
                Auth.logout().then(() => {
                    this.showUser = $scope.user = false;
                    this.threads = [];
                }).catch((error) => {
                    console.log('Error: ', error);
                });
            };
            this.getThreads = function (dir) {
                this.loaded = false;
                this.threads = [];
                if ($scope.user !== false && typeof($scope.user) !== 'undefined') {
                    if(dir == 'next') {
                        this.prevPageTokens.push(this.nextPageToken);
                    }
                    if(dir == 'back') {
                        this.prevPageTokens.pop();
                        this.nextPageToken = this.prevPageTokens[this.prevPageTokens.length - 1]
                    }
                    Threads.getThreads(this.nextPageToken).then((data) => {
                        console.log(data)
                        angular.forEach(data.threads, function(value, key) {
                          this[key].isCollapsed = true;
                        }, data.threads);
                        this.threads = data.threads;
                        this.nextPageToken = data.nextPageToken;
                        this.loaded = true;
                    }).catch((error) => {
                        this.showUser = this.loaded = this.nextPageToken = false;
                        this.threads = this.prevPageTokens = [];
                        Auth.logout();
                        console.log('Error: ', error);
                    });
                }
            };
            $scope.$watch('user', () => {
                if ($scope.user !== false && typeof($scope.user) !== 'undefined') {
                    this.getThreads('next');
                }
            });
        }
    ]
};

angular.module('gmailApp')
    .component('appComponent', appComponent)