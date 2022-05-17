-- phpMyAdmin SQL Dump
-- version 4.9.2
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1:3306
-- Generation Time: Apr 14, 2021 at 08:24 AM
-- Server version: 8.0.18
-- PHP Version: 7.4.0

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `is213_medication_info`
--
CREATE DATABASE IF NOT EXISTS `is213_medication_info` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
USE `is213_medication_info`;

-- --------------------------------------------------------

--
-- Table structure for table `medication_info`
--

DROP TABLE IF EXISTS `medication_info`;
CREATE TABLE IF NOT EXISTS `medication_info` (
  `med_id` char(4) NOT NULL,
  `med_name` varchar(20) NOT NULL,
  `med_price` decimal(10,2) NOT NULL,
  PRIMARY KEY (`med_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `medication_info`
--

INSERT INTO `medication_info` (`med_id`, `med_name`, `med_price`) VALUES
('1001', 'Lisinopril', '16.00'),
('1002', 'Atorvastatin', '19.70'),
('1003', 'Levothyroxine', '15.00'),
('1004', 'Metformin', '15.50'),
('1005', 'Amlodipine', '58.00'),
('1006', 'Metoprolol', '15.50'),
('1007', 'Omeprazole', '7.20'),
('1008', 'Simvastatin', '16.00'),
('1009', 'Losartan', '16.40'),
('1010', 'Clonidine', '7.80');
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
