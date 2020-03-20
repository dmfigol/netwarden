<template>
  <div>
    <b-table :data="rows" :columns="columns"></b-table>
  </div>
</template>

<script>
import axios from "axios";
export default {
  name: "Inventory",
  props: {},
  data() {
    return {
      rows_old: [
        {
          "name": "R1",
          "site": "Krakow",
          "fqdn": "r1.krk.lab.dmfigol.me",
          "mgmt_ip": "192.168.153.101",
          "sw_version": "N/A",
          "credentials": "cisco/cisco",
          "console_url": "<a href='telnet://192.168.153.100:9000' target='_blank'>telnet://192.168.153.100:9000</a>",
        },
      ],
      rows: [],
      columns: [
        {
          field: "name",
          label: "Name",
          // width: "40",
          // numeric: true,
        },
        {
          field: "site",
          label: "Site",
        },
        {
          field: "fqdn",
          label: "FQDN",
        },
        {
          field: "mgmt_ip",
          label: "Management IP",
          // centered: true,
        },
        {
          field: "sw_version",
          label: "Software Version",
        },
        {
          field: "credentials",
          label: "Credentials",
        },
        {
          field: "console_url",
          label: "Console",
          renderHtml: true,
        },
      ],
    };
  },
  mounted () {
    axios
      .get('http://192.168.153.100:8000/devices')
      .then(response => {
        console.log(response.data[0]);
        for (let device of response.data) {
          device.credentials = `${device.username}/${device.password}`;
          let console_url = `telnet://${device.console.server}:${device.console.port}`;
          device.console_url = `<a href='${console_url}'>${console_url}</a>`;
        }
        this.rows = response.data;
      })
  }
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="scss">
h3 {
  margin: 40px 0 0;
}
ul {
  list-style-type: none;
  padding: 0;
}
li {
  display: inline-block;
  margin: 0 10px;
}
a {
  color: #42b983;
}
</style>
