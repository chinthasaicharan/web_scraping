-- phpMyAdmin SQL Dump
-- version 4.9.2
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1:3306
-- Generation Time: Nov 28, 2022 at 04:53 PM
-- Server version: 10.4.10-MariaDB
-- PHP Version: 7.3.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `output`
--

-- --------------------------------------------------------

--
-- Table structure for table `deals_scrapped_data`
--

DROP TABLE IF EXISTS `deals_scrapped_data`;
CREATE TABLE IF NOT EXISTS `deals_scrapped_data` (
  `deal_id` int(11) NOT NULL AUTO_INCREMENT,
  `deal_source_website` varchar(30) CHARACTER SET utf8mb4 DEFAULT NULL,
  `deal_source_website_url` varchar(300) CHARACTER SET utf8mb4 DEFAULT NULL,
  `deal_title` varchar(300) CHARACTER SET utf8mb4 DEFAULT NULL,
  `deal_store` varchar(30) CHARACTER SET utf8mb4 DEFAULT NULL,
  `deal_url` varchar(300) CHARACTER SET utf8mb4 DEFAULT NULL,
  `deal_url_cleaned` varchar(300) CHARACTER SET utf8mb4 DEFAULT NULL,
  `deal_views` int(6) DEFAULT NULL,
  `deal_likes` int(6) DEFAULT NULL,
  `deal_hotness` int(6) DEFAULT NULL,
  `deal_original_price` int(11) DEFAULT NULL,
  `deal_price` int(11) DEFAULT NULL,
  `deal_discount_percentage` int(11) DEFAULT NULL,
  `deal_start_date` date DEFAULT NULL,
  `deal_start_time` time DEFAULT NULL,
  `deal_end_date` date DEFAULT NULL,
  `deal_end_time` time DEFAULT NULL,
  `deal_is_hot` int(3) DEFAULT NULL,
  `deal_is_active` int(3) DEFAULT NULL,
  `deal_category` varchar(100) CHARACTER SET utf8mb4 DEFAULT NULL,
  `deal_image` varchar(200) CHARACTER SET utf8mb4 DEFAULT NULL,
  `deal_is_featured` int(3) DEFAULT NULL,
  `deal_short_description` varchar(300) CHARACTER SET utf8mb4 DEFAULT NULL,
  `deal_description` varchar(3000) CHARACTER SET utf8mb4 DEFAULT NULL,
  `record_creation_datetime` datetime NOT NULL DEFAULT current_timestamp(),
  `record_updation_datetime` datetime NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `issue_found` varchar(20) CHARACTER SET utf8mb4 NOT NULL,
  `issue_details` varchar(200) CHARACTER SET utf8mb4 NOT NULL,
  PRIMARY KEY (`deal_id`)
) ENGINE=InnoDB AUTO_INCREMENT=110 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
