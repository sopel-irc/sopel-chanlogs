# sopel-chanlogs

A channel logging plugin for Sopel IRC bots

## Installing

Releases are hosted on PyPI, so after installing Sopel, all you need is `pip`:

```shell
$ pip install sopel-chanlogs
```

Enable the plugin with `sopel-plugins enable chanlogs`, if your bot
configuration requires it.

### Requirements

`sopel-chanlogs` requires only Sopel itself, version 7.1 or higher.

## Usage

### Configuration

The easiest way to configure `sopel-chanlogs` is via Sopel's configuration
wizard—simply run `sopel-plugins configure chanlogs` and complete the prompts.
All settings are optional, falling back on sensible defaults.

<dl>
  <dt>
    <tt>dir</tt>
  </dt>
  <dd>
    Path to channel log storage directory. Default: <tt>~/chanlogs</tt>
  </dd>
  <dt>
    <tt>by_day</tt>
  </dt>
  <dd>
    Split log files by day. Default: <tt>True</tt>
  </dd>
  <dt>
    <tt>privmsg</tt>
  </dt>
  <dd>
    Record private messages. Default: <tt>False</tt>
  </dd>
  <dt>
    <tt>microseconds</tt>
  </dt>
  <dd>
    Include microseconds in log timestamps. Default: <tt>False</tt>
  </dd>
  <dt>
    <tt>localtime</tt>
  </dt>
  <dd>
    <p>
      Attempt to use preferred timezone (the bot's
      <tt>core.default_timezone</tt>) instead of UTC. Default: <tt>False</tt>
    </p>
    <p>
      <em>
        <strong>Please note</strong> that Sopel's default
        <tt>default_timezone</tt> is UTC.
      </em>
    </p>
  </dd>
</dl>

#### Advanced configuration

Log line templates can be overridden using the relevant setting from this list:

- `message_template`
- `action_template`
- `join_template`
- `part_template`
- `quit_template`
- `nick_template`
- `topic_template`

Each template is formatted using the following `{placeholder}` values:

- the `trigger`, with all of its attributes (see [Sopel's
  documentation](https://sopel.chat/docs/trigger.html))
- the `date` in ISO format
- the `time` in ISO format
- the full `datetime` in ISO format

For convenience, the `message_template` also receives a `message` placeholder.

Please consult the plugin's code for current default templates.
