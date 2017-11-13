#!/usr/bin/env ruby
# Author: Franccesco Orozco.
# Version: 0.1.0
# This program extracts Subject Alternative Names from SSL Certificates
# which it can disclose virtual names the server has... so stop doing so many
# dns brute force for the love of god. This can also provide you with email
# addresses, URI's and IP addresses.
#
# Usage: getaltname.rb -h [host] -p [ssl_port]
#
# MIT License
#
# Copyright (c) [2017] [Franccesco Orozco]
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

require 'socket'
require 'openssl'
require 'optparse'

# defining options for host and port (with 443 as default)
options = { host: nil, port: 443 }

ARGV.options do |opts|
  opts.banner = "Usage:  #{File.basename($PROGRAM_NAME)} [OPTIONS]"

  opts.separator ''
  opts.separator 'Specific Options:'

  opts.on('-h', '--host host', String,
          'Host to extract alternative names.') do |host|
    options[:host] = host
  end

  opts.separator 'Common Options:'

  opts.on('-p', '--port port', Integer,
          'Port to connect to (default 443)') do |port|
    options[:port] = port
  end
  opts.on('--help', 'Show this message.') do
    puts opts
    exit
  end

  begin
    opts.parse!
  rescue StandardError
    puts opts
    exit
  end
end

# if a hostname wasn't specified then ask for it.
if options[:host].nil?
  print 'Hostname: '
  options[:host] = gets.chomp
end

# creating a connection and requesting the certificate
client_connection = TCPSocket.new(options[:host], options[:port])
ssl_connection = OpenSSL::SSL::SSLSocket.new(client_connection).connect
cert = OpenSSL::X509::Certificate.new(ssl_connection.peer_cert)

# closing coms
ssl_connection.sysclose
client_connection.close

# store only the values of 'subjectAltName' in san variable
san = cert.extensions.find { |value| value.oid == 'subjectAltName' }

# format values and display them in a list so we can use them in other tools
# and for copy&paste supah-powah... output is on the way.
begin
  san = san.value.split(', ')
rescue StandardError
  puts 'No Alternative Names found.'
else
  # cut 'DNS:' from every entry, bad implement but it works right now
  puts "#{san.length} Subject Alternative Names found:"
  puts '=================================='
  san.each { |value| puts value[4..-1] }
end
