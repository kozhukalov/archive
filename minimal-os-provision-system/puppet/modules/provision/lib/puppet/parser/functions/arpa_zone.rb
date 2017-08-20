module Puppet::Parser::Functions
  newfunction(:arpa_zone, :type => :rvalue) do |args|
    args[0].split(".").reverse.inject(""){|_, octet| _ << octet + "."} << "in-addr.arpa"
  end
end
