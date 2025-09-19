ActionMailer::Base.smtp_settings = {
  address: ENV.fetch("SMTP_ADDRESS", "mailhog"),
  port: ENV.fetch("SMTP_PORT", 1025).to_i,
  domain: ENV.fetch("SMTP_DOMAIN", "localhost"),
  user_name: ENV.fetch("SMTP_USERNAME", "").presence,
  password: ENV.fetch("SMTP_PASSWORD", "").presence,
  authentication: ENV.fetch("SMTP_AUTHENTICATION", "plain").presence,
  enable_starttls_auto: ENV.fetch("SMTP_ENABLE_STARTTLS_AUTO", "false") == "true",
  openssl_verify_mode: ENV.fetch("SMTP_OPENSSL_VERIFY_MODE", "none"),
  ssl: ENV.fetch("SMTP_SSL", "false") == "true",
  tls: ENV.fetch("SMTP_TLS", "false") == "true"
}

ActionMailer::Base.delivery_method = :smtp
ActionMailer::Base.default_url_options = { host: ENV["FRONTEND_URL"] }
ActionMailer::Base.asset_host = ENV["FRONTEND_URL"]
