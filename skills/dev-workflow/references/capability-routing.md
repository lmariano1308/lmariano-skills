# Optional capability routing

Use optional stack skills only when they are already available. Never install one during a task.

| Capability | Preferred skill names | Fallback when absent |
|---|---|---|
| Go backend | `go-engineering` | Repository rules and native project commands |
| Angular frontend | `angular` | Repository rules and native project commands |
| PostgreSQL | `postgresql` | Repository rules and native project commands |
| MongoDB | `mongodb` | Repository rules and native project commands |
| Redis | `redis` | Repository rules and native project commands |
| Visual validation | `webapp-testing` | Available local browser or manual evidence supplied by the user |

Announce whether the preferred capability was loaded or the fallback was selected. Capability absence must not block read-only investigation and must not trigger installation.
