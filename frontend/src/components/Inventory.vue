<template>
  <container>
    <h1 class="title has-text-centered">Inventory</h1>
    <b-table
      :data="rows"
      ref="table"
      :opened-detailed="defaultOpenedDetails"
      detailed
      detail-key="name"
      :show-detail-icon="showDetailIcon"
      :columns="columns"
    >
      <template slot="detail" slot-scope="props">
        <article class="media">
          <div class="media-content">
            <div class="content">
              <!--<p>
                        <strong>{{ props.row.name }}</strong>
                        <br>
                        Lorem ipsum dolor sit amet, consectetur adipiscing elit.
                        Proin ornare magna eros, eu pellentesque tortor vestibulum ut.
                        Maecenas non massa sem. Etiam finibus odio quis feugiat facilisis.
                    </p>-->
              <b-dropdown :triggers="['hover']" aria-role="list">
                <button class="button is-info" slot="trigger">
                  <span>Retrieve config</span>
                  <b-icon icon="menu-down"></b-icon>
                </button>

                <b-dropdown-item
                  aria-role="listitem"
                  @click="get_cfg(props.row.name, 'ssh')"
                  >Plain text</b-dropdown-item
                >
                <b-dropdown-item
                  aria-role="listitem"
                  @click="get_cfg(props.row.name, 'netconf')"
                  >NETCONF XML</b-dropdown-item
                >
                <b-dropdown-item
                  aria-role="listitem"
                  @click="get_cfg(props.row.name, 'restconf')"
                  >RESTCONF JSON</b-dropdown-item
                >
              </b-dropdown>
            </div>
          </div>
        </article>
      </template>
    </b-table>

    <b-modal ref="cfg" v-model="isCFGModalActive">
      <pre lang="json">{{ cfg }}</pre>
    </b-modal>
  </container>
</template>

<script>
import axios from "axios";
export default {
  name: "Inventory",
  props: {},
  data() {
    return {
      rows: [],
      defaultOpenedDetails: [1],
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
        // {
        //   field: "fqdn",
        //   label: "FQDN",
        // },
        // {
        //   field: "mgmt_ip",
        //   label: "Management IP",
        //   // centered: true,
        // },
        {
          field: "vendor",
          label: "Vendor",
        },
        {
          field: "model",
          label: "Model",
        },
        {
          field: "software_version",
          label: "Software Version",
        },
        {
          field: "serial_number",
          label: "Serial Number",
        },
        // {
        //   field: "credentials",
        //   label: "Credentials",
        // },
        // {
        //   field: "console_url",
        //   label: "Console",
        //   renderHtml: true,
        // },
        // {
        //   field: "cfg",
        //   label: "Config",
        //   renderHtml: true,
        // },
      ],
      isCFGModalActive: false,
      cfg: "",
      platform_map: {
        cisco_iosxe: "Cisco IOS-XE",
      }
    };
  },
  methods: {
    get_cfg(device, connection = "ssh") {
      this.cfg = "";
      // this.isCFGModalActive = true;
      const loadingComponent = this.$buefy.loading.open({
        container: null,
      });
      axios
        .get(`/api/devices/${device}/cfg?connection=${connection}`)
        .then((response) => {
          this.isCFGModalActive = true;
          let cfg = response.data.cfg;
          if (typeof cfg === "object") this.cfg = JSON.stringify(cfg, null, 2);
          else this.cfg = cfg;
          loadingComponent.close();
        });
    },
  },
  mounted() {
    axios.get("/api/devices").then((response) => {
      console.log(response.data[0]);
      for (let device of response.data) {
        // device.credentials = `${device.username}/${device.password}`;
        // let console_url = `telnet://${device.console.server}:${device.console.port}`;
        // device.console_url = `<a href='${console_url}'>${console_url}</a>`;
        let platform = this.platform_map[device.platform];
        device.software_version = `${platform} ${device.software_version}`;
      }
      this.rows = response.data;
    });
  },
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="scss">
pre {
  text-align: left;
}
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
pre {
  font-family: "Menlo", "Consolas", "Courier New", Courier, monospace;
}

textarea {
  border: none;
  font-size: 20px;
  resize: none;

  font-family: "monospace";
}
</style>
