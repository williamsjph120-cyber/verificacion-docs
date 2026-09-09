-- Seed: Create default admin user
-- Password: admin123

INSERT INTO users (email, password_hash, full_name, role) VALUES (
    'admin@test.com',
    '$2b$12$LJ3m4ys3Lz0QvWq3Kzq3YOeV7RzX5y5y5y5y5y5y5y5y5y5y5y5y',
    'Administrador',
    'admin'
) ON CONFLICT (email) DO NOTHING;
