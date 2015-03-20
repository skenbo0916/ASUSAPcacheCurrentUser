#!/usr/bin/perl
use strict;

use MIME::Base64;
use JSON;

BEGIN {
    use getCpanModule;
    getCpanModule::loadCpanModule( 'WWW', 'Mechanize', 'http://cpansearch.perl.org/src/ETHER/WWW-Mechanize-1.74/lib/WWW/Mechanize.pm' );
}
use WWW::Mechanize;

our $host = ''; # fill in your host name or static IP address
our $port = 80; # change port by your setting
our $username = ''; # fill in your admin. username
our $password = ''; # fill in your password

fetch();

sub fetch {
    my $mech = WWW::Mechanize->new( onerror => undef, onwarn => \&Carp::carp, );

    $mech->add_header( 'Accept' => 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8' );
    $mech->add_header( 'Accept-Encoding' => 'gzip, deflate, sdch' );
    $mech->add_header( 'Accept-Language' => 'zh-TW,zh;q=0.8,en-US;q=0.6,en;q=0.4' );
    $mech->add_header( 'Authorization' => 'Basic '.encode_base64("$username:$password") );
    $mech->add_header( 'Cache-Control' => 'max-age=0' );
    $mech->add_header( 'Connection' => 'keep-alive' );
    $mech->add_header( 'Host' => "http://$host:$port" );
    $mech->add_header( 'Referer' => "$host:$port" );
    $mech->add_header( 'User-Agent' => 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.115 Safari/537.36' );

    $mech->get( "$host:$port" );

    $mech->post( "http://$host:$port/device-map/apply.cgi", {
        action_mode => 'refresh_networkmap',
        action_script => '',
        action_wait => '5',
        current_page => 'device-map/clients.asp',
        next_page => 'device-map/clients.asp',
    } );

    $mech->get( "http://$host:$port/getdhcpLeaseInfo.asp" );
    my $oriString = $mech->content();
    my $MACdeviceMap = {};
    while( $oriString =~ /<mac>value=(.*?)<\/mac>\n<hostname>value=(.*?)<\/hostname>/g ) {
        $MACdeviceMap->{uc $1} = $2;
    }

    $mech->get( "http://$host:$port/update_clients.asp" );
    my $oriString = $mech->content();
    my $onlineUser = [];
    my( $devicesStrRaw ) = $oriString =~ /client_list_array = '(.*)';/;
    while( $devicesStrRaw =~ /<6>(.*?)>(.*?)>(.*?)>0>0>0/g ) {
        push @$onlineUser, {
            user => $MACdeviceMap->{$3},
            ip => $2,
            MAC => $3,
        };
    }

    $mech->get( "http://$host:$port/Logout.asp" );

    print JSON::encode_json( $onlineUser );
}
