-- Tạo bảng tbl_user
use traffic_sign;

CREATE TABLE tbl_user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100),
    address varchar(100),
    role varchar(100),
    created_date DATETIME,
    created_by varchar(100)
);

-- Tạo bảng tbl_traffic_sign
CREATE TABLE tbl_traffic_sign (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    code VARCHAR(50),
    description VARCHAR(500),
    created_date DATETIME,
    created_by varchar(100),
    path VARCHAR(255)
);

-- Tạo bảng tbl_sample
CREATE TABLE tbl_sample (
    id INT AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(50),
    path VARCHAR(255),
    name VARCHAR(100),
    created_date DATETIME,
    created_by varchar(100)
);

-- Tạo bảng tbl_label
CREATE TABLE tbl_label (
    id INT AUTO_INCREMENT PRIMARY KEY,
    centerX DOUBLE,
    centerY DOUBLE,
    height DOUBLE,
    width DOUBLE,
    created_date DATETIME,
    created_by varchar(100),
    traffic_sign_id INT,
    sample_id INT,
    FOREIGN KEY (traffic_sign_id) REFERENCES tbl_traffic_sign(id),
    FOREIGN KEY (sample_id) REFERENCES tbl_sample(id)
);



-- Tạo bảng tbl_model
CREATE TABLE tbl_model (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    path VARCHAR(255),
    date DATE,
    acc DOUBLE,
    pre DOUBLE,
    f1 DOUBLE,
    recall DOUBLE,
    status VARCHAR(50),
    created_date DATETIME,
    created_by varchar(100)
);

-- Tạo bảng tbl_model_sample
CREATE TABLE tbl_model_sample (
    id INT AUTO_INCREMENT PRIMARY KEY,
    model_id INT,
    sample_id INT,
    created_date DATETIME,
    created_by varchar(100),
    FOREIGN KEY (model_id) REFERENCES tbl_model(id),
    FOREIGN KEY (sample_id) REFERENCES tbl_sample(id)
);

INSERT INTO `traffic_sign`.`tbl_traffic_sign` (`id`, `name`, `code`, `description`, `created_date`, `created_by`, `path`) VALUES (0, 'Cấm đi ngược chiều', 'cam_di_nguoc_chieu', 'Biển báo này chỉ dẫn phương tiện không được phép di chuyển ngược chiều. Phạm vi áp dụng cho các đường một chiều và khu vực giao thông hạn chế.', '2024-10-03 01:00:40', 'duydb', 'https://bizweb.dktcdn.net/100/352/036/files/bien-bao-duong-cam.jpg?v=1575703786352');
INSERT INTO `traffic_sign`.`tbl_traffic_sign` (`id`, `name`, `code`, `description`, `created_date`, `created_by`, `path`) VALUES (1, 'Cấm dừng và đỗ xe', 'cam_dung_va_do_xe', 'Biển báo này quy định các phương tiện không được dừng hoặc đỗ tại vị trí đặt biển, nhằm đảm bảo lưu thông thông thoáng và an toàn cho khu vực.', '2024-10-03 01:00:40', 'duydb', 'https://thietbigiaothong247.com/wp-content/uploads/2017/04/bien-cam-di-nguoc-chieu.jpg');
INSERT INTO `traffic_sign`.`tbl_traffic_sign` (`id`, `name`, `code`, `description`, `created_date`, `created_by`, `path`) VALUES (2, 'Cấm rẽ trái', 'cam_re_trai', 'Biển này yêu cầu tất cả các phương tiện không được phép rẽ trái tại ngã tư hoặc vị trí cụ thể để tránh xung đột giao thông và tai nạn.', '2024-10-03 01:00:40', 'duydb', 'https://carpla.vn/blog/wp-content/uploads/2023/12/y-nghia-bien-cam-dung-do.jpg');
INSERT INTO `traffic_sign`.`tbl_traffic_sign` (`id`, `name`, `code`, `description`, `created_date`, `created_by`, `path`) VALUES (3, 'Giới hạn tốc độ', 'gioi_han_toc_do', 'Biển báo này quy định tốc độ tối đa cho phép mà các phương tiện có thể di chuyển trong khu vực hoặc đoạn đường được chỉ định, nhằm bảo đảm an toàn giao thông.', '2024-10-03 01:00:40', 'duydb', 'https://cdn.pixabay.com/photo/2013/07/13/13/16/no-parking-160693_1280.png');
INSERT INTO `traffic_sign`.`tbl_traffic_sign` (`id`, `name`, `code`, `description`, `created_date`, `created_by`, `path`) VALUES (4, 'Biển báo cấm', 'bien_bao_cam', 'Biển này thông báo một lệnh cấm chung cho các phương tiện hoặc hành vi cụ thể như cấm xe máy, xe tải, hoặc cấm vượt tại khu vực nhất định.', '2024-10-03 01:00:40', 'duydb', 'https://cdn.thuvienphapluat.vn/uploads/Hoidapphapluat/2024/DKV/tuan-3-thang-3/bien-cam-xe-may.jpg');
INSERT INTO `traffic_sign`.`tbl_traffic_sign` (`id`, `name`, `code`, `description`, `created_date`, `created_by`, `path`) VALUES (5, 'Biển báo nguy hiểm', 'bien_nguy_hiem', 'Biển này cảnh báo các tình huống giao thông nguy hiểm như đường cong gấp, lối đi có dốc lớn, hoặc khu vực dễ sạt lở, yêu cầu các tài xế giảm tốc độ và chú ý quan sát.', '2024-10-03 01:00:40', 'duydb', 'https://hoclaixe83.com/wp-content/uploads/105-cam-oto-va-moto-1.jpg');
INSERT INTO `traffic_sign`.`tbl_traffic_sign` (`id`, `name`, `code`, `description`, `created_date`, `created_by`, `path`) VALUES (6, 'Biển hiệu lệnh', 'bien_hieu_lenh', 'Biển này chỉ dẫn bắt buộc về hướng đi hoặc hành vi mà người điều khiển phương tiện cần tuân thủ, như đi thẳng, rẽ phải, hoặc đi vào khu vực hạn chế.', '2024-10-03 01:00:40', 'duydb', 'https://hoclaixe83.com/wp-content/uploads/105-cam-oto-va-moto-1.jpg');
