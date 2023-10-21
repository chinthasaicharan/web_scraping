-- phpMyAdmin SQL Dump
-- version 4.9.2
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1:3306
-- Generation Time: Nov 29, 2022 at 03:56 PM
-- Server version: 10.4.10-MariaDB
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
-- Database: `output`
--

-- --------------------------------------------------------

--
-- Table structure for table `coupons_scrapped_data`
--

DROP TABLE IF EXISTS `coupons_scrapped_data`;
CREATE TABLE IF NOT EXISTS `coupons_scrapped_data` (
  `coupon_id` int(11) NOT NULL AUTO_INCREMENT,
  `coupon_title` varchar(200) NOT NULL,
  `coupon_source_website` int(30) NOT NULL,
  `coupon_source_url` varchar(300) DEFAULT NULL,
  `coupon_url` varchar(300) DEFAULT NULL,
  `coupon_unique_id` varchar(30) DEFAULT NULL,
  `coupon_code` varchar(40) DEFAULT NULL,
  `coupon_store` varchar(20) DEFAULT NULL,
  `coupon_is_verified` varchar(3) NOT NULL,
  `coupon_verified_datetime` datetime DEFAULT NULL,
  `coupon_is_active` int(1) DEFAULT NULL,
  `coupon_start_date` date DEFAULT NULL,
  `coupon_end_date` date DEFAULT NULL,
  `coupon_success_rate` int(3) DEFAULT NULL,
  `coupon_is_code_required` int(3) DEFAULT NULL,
  `coupon_users_redeemed` int(6) DEFAULT NULL,
  `coupon_likes` int(6) DEFAULT NULL,
  `coupon_description` varchar(5000) DEFAULT NULL,
  `record_creation_datetime` datetime NOT NULL DEFAULT current_timestamp(),
  `record_updation_datetime` datetime NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`coupon_id`)
) ENGINE=InnoDB AUTO_INCREMENT=250 DEFAULT CHARSET=utf8mb4;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
