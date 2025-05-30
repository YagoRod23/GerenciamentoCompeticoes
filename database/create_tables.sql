-- Sistema de Gestão de Competições Esportivas Universitárias
-- Criação das tabelas principais

SET FOREIGN_KEY_CHECKS = 0;

-- Tabela de usuários
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    user_type ENUM('master', 'organization', 'public') NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Tabela de locais
CREATE TABLE IF NOT EXISTS venues (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    address TEXT,
    capacity INT,
    sports_available SET('basketball', 'futsal', 'volleyball', 'handball') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Tabela de competições
CREATE TABLE IF NOT EXISTS competitions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    sport ENUM('basketball', 'futsal', 'volleyball', 'handball') NOT NULL,
    format_type ENUM('elimination', 'best_of_three', 'swiss', 'groups_playoffs', 'round_robin', 'other') NOT NULL,
    start_date DATE,
    end_date DATE,
    status ENUM('planning', 'ongoing', 'finished') DEFAULT 'planning',
    max_teams INT DEFAULT 16,
    description TEXT,
    rules TEXT,
    created_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(id)
);

-- Tabela de equipes
CREATE TABLE IF NOT EXISTS teams (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    short_name VARCHAR(20),
    logo_path VARCHAR(255),
    primary_color VARCHAR(7),
    secondary_color VARCHAR(7),
    contact_person VARCHAR(100),
    contact_phone VARCHAR(20),
    contact_email VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Tabela de atletas
CREATE TABLE IF NOT EXISTS athletes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    team_id INT,
    name VARCHAR(100) NOT NULL,
    jersey_number INT,
    position VARCHAR(50),
    birth_date DATE,
    document_number VARCHAR(20),
    phone VARCHAR(20),
    email VARCHAR(100),
    emergency_contact VARCHAR(100),
    emergency_phone VARCHAR(20),
    is_captain BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (team_id) REFERENCES teams(id),
    UNIQUE KEY unique_jersey_team (team_id, jersey_number)
);

-- Tabela de comissão técnica
CREATE TABLE IF NOT EXISTS technical_staff (
    id INT AUTO_INCREMENT PRIMARY KEY,
    team_id INT,
    name VARCHAR(100) NOT NULL,
    role ENUM('head_coach', 'assistant_coach', 'physical_trainer', 'physiotherapist', 'manager') NOT NULL,
    document_number VARCHAR(20),
    phone VARCHAR(20),
    email VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (team_id) REFERENCES teams(id)
);

-- Tabela de inscrições de equipes em competições
CREATE TABLE IF NOT EXISTS team_registrations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    competition_id INT,
    team_id INT,
    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    group_name VARCHAR(10),
    seed_position INT,
    is_confirmed BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (competition_id) REFERENCES competitions(id),
    FOREIGN KEY (team_id) REFERENCES teams(id),
    UNIQUE KEY unique_team_competition (competition_id, team_id)
);

-- Tabela de jogos
CREATE TABLE IF NOT EXISTS games (
    id INT AUTO_INCREMENT PRIMARY KEY,
    competition_id INT,
    home_team_id INT,
    away_team_id INT,
    venue_id INT,
    game_date DATETIME,
    round_number INT,
    phase VARCHAR(50),
    status ENUM('scheduled', 'ongoing', 'finished', 'postponed', 'cancelled') DEFAULT 'scheduled',
    home_score INT DEFAULT 0,
    away_score INT DEFAULT 0,
    home_sets INT DEFAULT 0,
    away_sets INT DEFAULT 0,
    observations TEXT,
    referee_name VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (competition_id) REFERENCES competitions(id),
    FOREIGN KEY (home_team_id) REFERENCES teams(id),
    FOREIGN KEY (away_team_id) REFERENCES teams(id),
    FOREIGN KEY (venue_id) REFERENCES venues(id)
);

-- Tabela de eventos do jogo (gols, cartões, pontos, etc.)
CREATE TABLE IF NOT EXISTS game_events (
    id INT AUTO_INCREMENT PRIMARY KEY,
    game_id INT,
    athlete_id INT,
    event_type ENUM('goal', 'point_2', 'point_3', 'free_throw', 'yellow_card', 'red_card', 'foul', 'substitution', 'set_point') NOT NULL,
    minute_occurred INT,
    set_number INT DEFAULT 1,
    points_value INT DEFAULT 1,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (game_id) REFERENCES games(id),
    FOREIGN KEY (athlete_id) REFERENCES athletes(id)
);

-- Tabela de suspensões
CREATE TABLE IF NOT EXISTS suspensions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    athlete_id INT,
    competition_id INT,
    suspension_type ENUM('yellow_cards', 'red_card', 'manual', 'disciplinary') NOT NULL,
    games_suspended INT NOT NULL,
    games_served INT DEFAULT 0,
    start_date DATE,
    end_date DATE,
    reason TEXT,
    created_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (athlete_id) REFERENCES athletes(id),
    FOREIGN KEY (competition_id) REFERENCES competitions(id),
    FOREIGN KEY (created_by) REFERENCES users(id)
);

-- Tabela de estatísticas por atleta e competição
CREATE TABLE IF NOT EXISTS athlete_statistics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    athlete_id INT,
    competition_id INT,
    games_played INT DEFAULT 0,
    goals_scored INT DEFAULT 0,
    points_scored INT DEFAULT 0,
    points_2 INT DEFAULT 0,
    points_3 INT DEFAULT 0,
    free_throws INT DEFAULT 0,
    yellow_cards INT DEFAULT 0,
    red_cards INT DEFAULT 0,
    fouls INT DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (athlete_id) REFERENCES athletes(id),
    FOREIGN KEY (competition_id) REFERENCES competitions(id),
    UNIQUE KEY unique_athlete_competition (athlete_id, competition_id)
);

-- Tabela de classificação
CREATE TABLE IF NOT EXISTS standings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    competition_id INT,
    team_id INT,
    games_played INT DEFAULT 0,
    wins INT DEFAULT 0,
    draws INT DEFAULT 0,
    losses INT DEFAULT 0,
    goals_for INT DEFAULT 0,
    goals_against INT DEFAULT 0,
    goal_difference INT DEFAULT 0,
    points INT DEFAULT 0,
    sets_for INT DEFAULT 0,
    sets_against INT DEFAULT 0,
    position INT DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (competition_id) REFERENCES competitions(id),
    FOREIGN KEY (team_id) REFERENCES teams(id),
    UNIQUE KEY unique_team_competition_standing (competition_id, team_id)
);

-- Inserir usuário master padrão
INSERT IGNORE INTO users (username, password_hash, user_type, full_name, email) 
VALUES ('admin', SHA2('admin123', 256), 'master', 'Administrador Master', 'admin@sistema.com');

-- Inserir locais padrão
INSERT IGNORE INTO venues (name, address, capacity, sports_available) VALUES 
('Ginásio Principal', 'Campus Universitário - Setor Esportivo', 500, 'basketball,futsal,volleyball,handball'),
('Quadra Externa 1', 'Campus Universitário - Área Externa', 200, 'basketball,futsal,volleyball'),
('Quadra Externa 2', 'Campus Universitário - Área Externa', 200, 'basketball,futsal,volleyball');

SET FOREIGN_KEY_CHECKS = 1;
