## network configuration
* Complex
* contains different groups of things:
  * stuff that is very similar across different devices (e.g. mgmt plane, restconf, netconf, vty configuration, dns, logging, netflow, ntp)
  * low level stuff that is different on different devices (e.g. ip address and other interface level configuration)
  * high level stuff which can be similar or different on diff devices - services (e.g. routing configuration or hsrp/vrrp or dmvpn or whatever). usually contains some lower level configuration stuff
* the intent of doing a config change can be sourced by:
  * network engineers - adjusting things based on the design, best practices, requirements which may result in some knobs to be touched
  * people who have no or minimal knowledge about network - they want to adjust network behavior as a whole? e.g. provisioning a new user (which may touch access ports on the switch, firewall rules, etc.), new MPLS VPN customer. "high-level services"

unanswered questions
* we need to know what configuration and in what form we want to store
  * what is the appropriate format?
  * db choice?
  * What goes to netbox vs our database?
  * 
* how is the final config created and applied
* do we store only elements needed to create configuration or final artifacts as well?
* how to rollback between different states?
* how to approach configuration change in a vendor agnostic fashion
* how do we a translate an arbitrary vendor independent parameter to a specific config "element" (line, xml child, whatever) for the chosen vendor
* how do we do pre and post config change verification


our solution
1. we want to retrieve and see configuration of a specific device at any time (different forms, e.g. plain text, RC in YAML?, NC XML - could take long, because netconf connection handler is needed)



workflow based config change 
bring new remote site
let's say we mostly use DMVPN and in this site, we will have a single router

1. device need to be added to netbox. - can easily be automated
2. need some day0 method to push config
3. assign a role, e.g. "DMVPN spoke"
 

we need "DMVPN spoke" role definition described in vendor independent form in our gui -> own our model if you will.
parametrized xml????? 
role (or service) "dmvpn spoke" data example, write YANG first!:

<dmvpn>
  <hub_overlay>$hub_overlay_ip</hub_overlay>
  <hub_underlay>$hub_underlay_ip</hub_underlay>
  <spoke_overlay>$spoke_overlay_ip</spoke_overlay>
  <multicast/>
</dmvpn>
{% include <eigrp-dmvpn> %}
for every yang leaf? we need a translation mechanism to the vendor accepted yang model (or even CLI if you want to go insane)

$hub_overlay_ip = {% first ip in the overlay subnet %}
$spoke_overlay_ip = {% next unallocated ip in the overlay subnet %}
dmvpn/hub_overlay for cisco iosxe will be native/dmvpn/.../.../

{
    "native": {
        "dmvpn":
        {
            "hub": $hub_overlay_ip
        }
    }
}

read yang data using some kind of yang library (like yangify?) to be able to manipulate result like this

1. define vendor-independent yang model for the service (e.g. dmvpn spoke)
2. parametrize some data which will be used in this model, define "function" to derive it and "description" for those
3. have a way to render it for the neteng (since yang is hard to understand)
4. have translation from every leaf of service yang (?) for every required NOS to a leaf data which is supported by that nos
5. mix all services into one and feed it to a yang manipulation library (e.g. yangify) together with vendor yang model
6. output will be resulting NC/RC config



logging: hosts and logging level

<logging>
 <server>
   <ip>1.2.3.4</ip>
   <ip>4.3.2.1</ip>
 <server>
 <level>info<level>
</logging>

> logging/server on cisco-ioxe native model
> logging/ip on some ACME vendor model 


<dmvpn>
  <hub_overlay>$hub_overlay_ip</hub_overlay>
  <hub_underlay>$hub_underlay_ip</hub_underlay>
  <spoke_overlay>$spoke_overlay_ip</spoke_overlay>
  <multicast/>
</dmvpn>
